from abc import ABC, abstractmethod
from json import loads as from_json, JSONDecodeError
from multiprocessing import Event, Process
from time import time
from pathlib import Path
from typing import Optional, Dict, Generator, Any

import arrow
import click
import psutil
from loguru import logger as log
from pydantic import ValidationError, RootModel, ConfigDict, AfterValidator
from pydantic.dataclasses import dataclass
from robotnikmq import RobotnikConfig
from typeguard import typechecked
from typing_extensions import Annotated

from legion_utils import broadcast_alert
from legion_utils.core import hostname, Priority, alert_key_str, broadcast_critical, broadcast_info
from legion_utils.princeps.config import SystemPrincepsConfiguration, ServicePrincepsConfiguration, \
    PrincepsConfiguration, Report

DEFAULT_LEGION_RUN_DIR = Path("/var/run/legion/")
DEFAULT_PRINCEPS_RUN_DIR = DEFAULT_LEGION_RUN_DIR / 'princeps'
DEFAULT_SERVICE_REGISTRY_DIR = DEFAULT_PRINCEPS_RUN_DIR / 'service_registry'


def timestamp(v: Any) -> float:
    return float(v)


Timestamp = Annotated[float, AfterValidator(timestamp)]
TimeDelta = Annotated[float, AfterValidator(timestamp)]


@typechecked
def now() -> Timestamp:
    return Timestamp(time())


@typechecked
def humanize(ts: Timestamp) -> str:
    return arrow.get(ts).humanize()


class ServiceRegistryEntryABC(ABC):
    @abstractmethod
    def should_warn(self) -> bool:
        pass  # pragma: no cover

    @abstractmethod
    def should_error(self) -> bool:
        pass  # pragma: no cover

    @abstractmethod
    def should_critical(self) -> bool:
        pass  # pragma: no cover

    @abstractmethod
    def to_alert_contents(self) -> Dict[str, str]:
        pass  # pragma: no cover

    def should_alert(self) -> bool:
        return self.should_critical() or self.should_error() or self.should_warn()

    @staticmethod
    @abstractmethod
    def of_file(filepath: Path) -> 'ServiceRegistryEntryABC':
        pass  # pragma: no cover


@dataclass(frozen=True)
class InvalidServiceRegistryEntry(ServiceRegistryEntryABC):
    model_config = ConfigDict(extra='allow', arbitrary_types_allowed=True)
    from_file: Path

    @staticmethod
    def of_file(filepath: Path) -> 'InvalidServiceRegistryEntry':
        return InvalidServiceRegistryEntry(from_file=filepath)

    def to_alert_contents(self) -> Dict[str, str]:
        return {"from_file": str(self.from_file),
                "file_contents": self.from_file.open('r').read()}

    def should_critical(self) -> bool:
        return False

    def should_error(self) -> bool:
        return True

    def should_warn(self) -> bool:
        return False


@dataclass(frozen=True)
class ServiceRegistryEntry(ServiceRegistryEntryABC):
    model_config = ConfigDict(extra='allow', arbitrary_types_allowed=True)
    name: str
    last_checkin: Timestamp
    next_checkin_before: Timestamp
    alert_ttl: TimeDelta
    warn_after: Optional[TimeDelta] = None
    error_after: Optional[TimeDelta] = None
    critical_after: Optional[TimeDelta] = None
    from_file: Optional[Path] = None

    def should_warn(self) -> bool:
        return self.warn_after is not None and not self.should_error() and not self.should_critical() and (
                now() >= self.next_checkin_before + int(self.warn_after))

    def should_error(self) -> bool:
        """
        Note that this function enforces a default behavior that if warn, error, and critical timeouts are not set,
        then the error timeout is set to 0 meaning that an error will be published when a service does not check in
        before the appointed time.
        """
        if self.warn_after is None and self.error_after is None and self.critical_after is None:
            error_after = TimeDelta(0)
        else:
            error_after = self.error_after
        return error_after is not None and not self.should_critical() and now() >= self.next_checkin_before + int(
            error_after)

    def should_critical(self) -> bool:
        return self.critical_after is not None and now() >= self.next_checkin_before + int(
            self.critical_after)

    def to_alert_contents(self) -> Dict[str, str]:
        return {"service_name": self.name,
                "checkin_expected_by": self.next_checkin_before,
                "last_checkin": self.last_checkin,
                "time_since_last_checkin": humanize(self.last_checkin)} | (
            {"princeps_entry_filepath": self.from_file} if self.from_file else {})

    @staticmethod
    @typechecked
    def of_file(filepath: Path) -> 'ServiceRegistryEntry':
        return ServiceRegistryEntry(from_file=filepath, **from_json(filepath.open('r').read()))


@dataclass(frozen=True)
class RegistrarParams:
    name: str
    checkin_interval: TimeDelta
    alert_ttl: TimeDelta
    directory: Path = DEFAULT_SERVICE_REGISTRY_DIR
    warn_after: Optional[TimeDelta] = None
    error_after: Optional[TimeDelta] = None
    critical_after: Optional[TimeDelta] = None


@typechecked
class ServiceRegistrar:
    """
    This class is designed to be used by runners to publish service registry entry files and thereby "check-in" with
    Princeps.
    """

    def __init__(self,
                 name: str,
                 checkin_interval: TimeDelta,
                 alert_ttl: TimeDelta,
                 directory: Path,
                 warn_after: Optional[TimeDelta] = None,
                 error_after: Optional[TimeDelta] = None,
                 critical_after: Optional[TimeDelta] = None):
        self._name = name
        self._checkin_interval = checkin_interval
        self._directory = directory
        self._alert_ttl = alert_ttl
        self._warn_after = warn_after
        self._error_after = error_after
        self._critical_after = critical_after

    @property
    def filepath(self) -> Path:
        return self._directory / f'{self._name}.json'

    def _check_in(self, ) -> ServiceRegistryEntry:
        return ServiceRegistryEntry(name=self._name,
                                    last_checkin=now(),
                                    next_checkin_before=now() + int(self._checkin_interval),
                                    alert_ttl=self._alert_ttl,
                                    warn_after=self._warn_after,
                                    error_after=self._error_after,
                                    critical_after=self._critical_after)

    def check_in(self) -> None:
        self.filepath.open('w+').write(RootModel[ServiceRegistryEntry](self._check_in()).model_dump_json())

    @staticmethod
    def of(params: RegistrarParams) -> 'ServiceRegistrar':
        return ServiceRegistrar(name=params.name,
                                checkin_interval=params.checkin_interval,
                                directory=params.directory,
                                alert_ttl=params.alert_ttl,
                                warn_after=params.warn_after,
                                error_after=params.error_after,
                                critical_after=params.critical_after)


@typechecked
class ServiceRegistry:
    """
    Essentially, a directory where service entry files are kept, updated, and read from. The idea is that services
    instrumented with Legion will periodically write ServiceRegistryEntry objects are JSON files to this directory and
    princeps will periodically scan them for relevant information, compare that to the state of the world, and publish
    information or alerts as necessary.
    """

    def __init__(self, directory: Path):
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)
        self.last_alerted: Dict[str, Timestamp] = {}

    def delinquent_services(self) -> Generator[ServiceRegistryEntryABC, None, None]:
        for filepath in self.directory.iterdir():
            try:
                entry = ServiceRegistryEntry(**from_json(filepath.open('r').read()))
                if entry.should_alert():
                    yield entry
            except (ValidationError, JSONDecodeError):
                log.warning(f"Unable to load {filepath} as a service registry entry")
                yield InvalidServiceRegistryEntry(from_file=filepath)

    def is_empty(self) -> bool:
        return not any(f for f in self.directory.iterdir())


class StoppablePeriodic(ABC):
    def __init__(self, halt_flag: Event, period: TimeDelta):
        self.halt_flag = halt_flag
        self.period = period

    @abstractmethod
    def action(self) -> None:
        pass  # pragma: no cover

    def run(self) -> None:
        while 42:
            self.action()
            if self.halt_flag.wait(timeout=self.period):
                return None


@typechecked
class ServicePrinceps(StoppablePeriodic):
    """
    This class is responsible for gathering information on instrumented services which have not checked in within a
    given timeframe and are therefore delinquent.
    """

    def __init__(self, exchange: str, halt_flag: Event, directory: Path, reporting_period: int,
                 config: Optional[RobotnikConfig] = None):
        super().__init__(halt_flag=halt_flag, period=TimeDelta(reporting_period))
        self.exchange = exchange
        self.route = f'{hostname()}.princeps.services'
        self.registry = ServiceRegistry(directory)
        self.config = config

    def _broadcast_alert(self, entry: ServiceRegistryEntryABC, priority: Priority) -> None:
        if isinstance(entry, ServiceRegistryEntry):
            broadcast_alert(exchange=self.exchange,
                            route=self.route,
                            description=f"{entry.name} failed to check in at {arrow.get(entry.next_checkin_before)}",
                            alert_key=alert_key_str([hostname(), 'legion', 'princeps', 'checkin_failure', entry.name]),
                            contents=entry.to_alert_contents(),
                            ttl=int(entry.alert_ttl),
                            priority=priority,
                            config=self.config)
        elif isinstance(entry, InvalidServiceRegistryEntry):
            broadcast_alert(exchange=self.exchange,
                            route=self.route,
                            description=f"Invalid service registry entry file detected",
                            alert_key=alert_key_str([hostname(),
                                                     'legion',
                                                     'princeps',
                                                     'invalid_service_registry_entry']),
                            contents=entry.to_alert_contents(),
                            ttl=int(self.period * 3),
                            priority=priority,
                            config=self.config)

    def publish_warning(self, entry: ServiceRegistryEntryABC) -> None:
        self._broadcast_alert(entry, Priority.WARNING)

    def publish_error(self, entry: ServiceRegistryEntryABC) -> None:
        self._broadcast_alert(entry, Priority.ERROR)

    def publish_critical(self, entry: ServiceRegistryEntryABC) -> None:
        self._broadcast_alert(entry, Priority.CRITICAL)

    def alert_on_delinquent_services(self) -> None:
        for entry in self.registry.delinquent_services():
            if entry.should_critical():
                self.publish_critical(entry)
            elif entry.should_error():
                self.publish_error(entry)
            elif entry.should_warn():
                self.publish_warning(entry)
        if self.registry.is_empty():
            log.warning(f"Registry directory: {self.registry.directory} is empty, alerting...")
            broadcast_alert(exchange=self.exchange,
                            route=self.route,
                            description=f"Princeps service registry directory: {self.registry.directory} is empty",
                            alert_key=alert_key_str([hostname(), 'legion', 'princeps', 'empty_registry']),
                            contents={'directory': str(self.registry.directory)},
                            ttl=int(self.period * 3),
                            priority=Priority.WARNING,
                            config=self.config)

    def action(self) -> None:
        self.alert_on_delinquent_services()

    @staticmethod
    def of(exchange: str, halt_flag: Event, config: ServicePrincepsConfiguration,
           robotnikmq_config: Optional[RobotnikConfig]) -> 'ServicePrinceps':
        return ServicePrinceps(exchange=exchange,
                               halt_flag=halt_flag,
                               directory=config.directory,
                               reporting_period=config.reporting_period,
                               config=robotnikmq_config)


@typechecked
class SystemPrinceps(StoppablePeriodic):
    """
    A process that periodically polls for CPU/RAM/HDD usage information and publishes that information as well as
    relevant alerts about it. It also determines when a system needs a reboot and publishes an alert for that as well.
    """

    def __init__(self, exchange: str, halt_flag: Event, config: SystemPrincepsConfiguration,
                 robotnikmq_config: Optional[RobotnikConfig] = None):
        super().__init__(halt_flag=halt_flag, period=TimeDelta(config.reporting_period))
        self.exchange = exchange
        self.config = config
        self.route = f'{hostname()}.system.system_base_stats'
        self.robotnikmq_config = robotnikmq_config

    def alert_on_restart_required(self) -> None:
        log.info("Checking if restart is required... ")
        if (self.config.restart_required is not None) and (priority := self.config.restart_required.priority()):
            since = arrow.utcnow().shift(seconds=(psutil.boot_time() - time())).humanize()
            log.warning(
                f"This machine needs a reboot, it has been up since: {since}")
            broadcast_alert(exchange=self.exchange,
                            route=self.route,
                            description=f'Restart required: {hostname()}',
                            alert_key=alert_key_str([hostname(), 'restart_required']),
                            contents={'hostname': hostname(),
                                      'up_since': since,
                                      'boot_time': psutil.boot_time()},
                            ttl=int(self.period * 2),
                            priority=priority,
                            config=self.robotnikmq_config)

    def alert_on_disk_usage(self, reports: Report) -> None:
        for path in self.config.paths.keys():
            if not path.exists():
                log.warning("No disk is mounted at configured path: " + str(path))
                broadcast_critical(exchange=self.exchange,
                                   route=self.route,
                                   contents={'hostname': hostname(),
                                             'non_existent_path': path},
                                   desc=f'Disk mount at {path} on {hostname()} does not exist',
                                   alert_key=f'[{hostname()}][{path}][disk_does_not_exist]', ttl=int(self.period * 2))
            else:
                report = reports[str(path)]
                if priority := self.config.paths[path].alert_priority(report['percent']):
                    contents = {'hostname': hostname(),
                                'up_since': arrow.utcnow().shift(
                                    seconds=(psutil.boot_time() - time())).humanize(),
                                'boot_time': psutil.boot_time()}
                    log.info("Broadcasting alert: " + str(contents))
                    broadcast_alert(exchange=self.exchange,
                                    route=self.route,
                                    description=f'Disk mounted at {path} on {hostname()} is {report["percent"]}% full',
                                    alert_key=alert_key_str([hostname(), f'{path}', 'disk_usage_past_threshold']),
                                    contents=contents,
                                    ttl=int(self.period * 2),
                                    priority=priority,
                                    config=self.robotnikmq_config)

    def report_on_cpu_ram_disk_network(self) -> Report:
        report = self.config.cpu_ram_disk_network_report()
        log.info("Publishing: " + str(report))
        broadcast_info(exchange=self.exchange,
                       route=self.route,
                       contents=report)
        return report

    def action(self) -> None:
        report = self.report_on_cpu_ram_disk_network()
        self.alert_on_disk_usage(report)
        self.alert_on_restart_required()


# Todo: Implement the other princeps services and integrate them as subprocesses of a main princeps class
# class PingPrinceps(StoppablePeriodic):
#     ...


class Princeps:
    """
    This class is responsible for several key categories of basic legion information publishing and alerting. Each of
    these categories has their own Princeps defined above and is managed as an independent process by this class:
    1. Gathering information on instrumented services (such as those using the @service or @periodic decorators) and
       broadcasting alerts if they have not checked in by a given time.
    2. Publishing information on key system functions such as CPU/RAM/Disk usage (as well as relevant alerts).
    3. Publishing information about the results of pinging configured machines (thereby reporting on nearby network
       conditions).
    """

    def __init__(self, exchange: str,
                 services_config: ServicePrincepsConfiguration,
                 system_config: SystemPrincepsConfiguration,
                 robotnikmq_config: Optional[RobotnikConfig] = None):
        self.exchange = exchange
        self.halt_flag = Event()
        self.service_princeps = ServicePrinceps.of(exchange=self.exchange, halt_flag=self.halt_flag,
                                                   config=services_config, robotnikmq_config=robotnikmq_config)
        self.system_princeps = SystemPrinceps(exchange=self.exchange, halt_flag=self.halt_flag,
                                              config=system_config, robotnikmq_config=robotnikmq_config)
        self.service_princeps_proc = Process(target=self.service_princeps.run)
        self.system_princeps_proc = Process(target=self.system_princeps.run)

    @staticmethod
    def _terminate(proc: Process) -> None:
        proc.join(timeout=10)
        if proc.is_alive():
            proc.terminate()
            proc.join(timeout=5)
            if proc.is_alive():
                log.warning("Sub-process not responding, killing...")
                proc.kill()
                proc.join()

    def stop(self, *_) -> None:
        self.halt_flag.set()
        log.info("Stopping service monitoring sub-process...")
        self._terminate(self.service_princeps_proc)
        log.info("Service monitoring sub-process stopped.")
        log.info("Stopping system stats monitoring sub-process...")
        self._terminate(self.system_princeps_proc)
        log.info("System stats monitoring sub-process stopped.")

    def run(self) -> None:
        # configure signal handling
        # Todo: Figure out why this refuses to work as planned
        # signal(SIGINT, self.stop)
        # signal(SIGTERM, self.stop)
        log.info("Starting service monitoring sub-process...")
        self.service_princeps_proc.start()
        log.info("Service monitoring started.")
        log.info("Starting system stats monitoring sub-process...")
        self.system_princeps_proc.start()
        log.info("System stats monitoring started.")
        self.service_princeps_proc.join()
        self.system_princeps_proc.join()

    @staticmethod
    def of(config: PrincepsConfiguration, robotnikmq_config: Optional[RobotnikConfig]) -> 'Princeps':
        return Princeps(exchange=config.exchange, services_config=config.services, system_config=config.system,
                        robotnikmq_config=robotnikmq_config)


@click.command
@click.option('config_path', '-c', '--config',
              type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True,
                              allow_dash=False, path_type=Path), required=True, help="Path to princeps configuration")
# Todo: Support non-default robotnikmq config
# @click.option('robotnik_config_path', '-r', '--robotnik-config',
#               type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True,
#                               allow_dash=False, path_type=Path),
#               help="Path to RobotnikMQ configuration (defaults to /etc/robotnikmq/robotnikmq.yaml)")
# def cli(config_path: Path, robotnik_config_path: Optional[Path] = None):
def cli(config_path: Path):
    # Todo: Add support for parsing non-default robotnikmq config (which requires adding a nice of() method to it)
    Princeps.of(PrincepsConfiguration.of(config_path), robotnikmq_config=None).run()
