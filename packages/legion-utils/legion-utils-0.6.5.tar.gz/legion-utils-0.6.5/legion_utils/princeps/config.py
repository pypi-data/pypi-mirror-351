import re
from functools import cache, partial
from ipaddress import IPv4Network, ip_network, ip_address, IPv4Address
from pathlib import Path
from pprint import pprint
from typing import Optional, Annotated, Any, Callable, TypeVar

import psutil
from pydantic import BeforeValidator
from pydantic.dataclasses import dataclass
from typeguard import typechecked
from yaml import safe_load as from_yaml

from legion_utils import Priority, priority_of
from legion_utils.core import hostname


Report = dict[str, str | float | list[float] | dict[str, float]]


@dataclass(frozen=True)
class ServicePrincepsConfiguration:
    directory: Path
    reporting_period: int


@dataclass(frozen=True)
class PathReportingConfiguration:
    warning_threshold_percentage: Optional[float] = None
    error_threshold_percentage: Optional[float] = None
    critical_threshold_percentage: Optional[float] = None

    def alert_priority(self, percentage: float) -> Optional[Priority]:
        if self.critical_threshold_percentage is not None and self.critical_threshold_percentage < percentage:
            return Priority.CRITICAL
        elif self.error_threshold_percentage is not None and self.error_threshold_percentage < percentage:
            return Priority.ERROR
        elif self.warning_threshold_percentage is not None and self.warning_threshold_percentage < percentage:
            return Priority.WARNING
        else:
            return None


@dataclass(frozen=True)
class RestartRequiredConfiguration:
    path: Path
    severity: Annotated[Priority, BeforeValidator(priority_of)]

    @cache
    def priority(self) -> Optional[Priority]:
        return self.severity if self.path.exists() else None

    @cache
    def restart_required(self):
        return self.path.exists()


@typechecked
def is_global(x: str) -> bool:
    return x.lower() == 'global'


# Used to validate that a specific string is just the literal "global"
Global = Annotated[str, BeforeValidator(is_global)]


@typechecked
def valid_source(candidate: Any) -> IPv4Network | Global:
    match candidate:
        case str() if is_global(candidate):
            return Global(candidate)
        case str():
            return ip_network(candidate)
    raise ValueError(f"The source value: '{str(candidate)}' is neither an IP address nor 'global'.")


T = TypeVar("T")


@typechecked
def _valid(func: Callable, *args, **kwargs) -> bool:
    try:
        return bool(func(*args, **kwargs))
    except ValueError:
        return False


@typechecked
def ip_address_or_hostname(candidate: Any) -> IPv4Address | str:
    _ip_addr = partial(_valid, ip_address)

    match candidate:
        case str() if _ip_addr(candidate):
            return ip_address(candidate)
        case str() if not bool(re.search(r"\s", candidate)):  # hostname without whitespace
            return candidate
        case _:
            raise ValueError(f"'{str(candidate)}' is neither a valid IP address, nor a hostname")

@dataclass(frozen=True)
class PingableConfiguration:
    """Indicates that the host should be pingable at a specific address if the source matches one of a given
       list of criteria. For example: {at: google.com, source: global} indicates that google.com should be
       pingable from any address, while {at: 192.168.86.123, source: [192.168.86.0/24, 10.0.0.0/24]} indicates
       that 192.168.86.123 should be pingable from either the 192.168.86.0/24 (LAN) subnet, or the 10.0.0.0/24 (VPN)
       subnet.

       The idea is that all machines should publish this information about themselves (alerts are fired if this
       information is not configured) and then, nodes that do the work of pinging will confirm that the machines are
       accessible from the parts of the internet where they claim they should be accessible from."""
    at: Annotated[IPv4Address | str, BeforeValidator(ip_address_or_hostname)]
    source: list[Annotated[IPv4Network | str, BeforeValidator(valid_source)]]


@dataclass(frozen=True)
class SystemPrincepsConfiguration:
    paths: dict[Path, PathReportingConfiguration]
    reporting_period: int = 30
    restart_required: Optional[RestartRequiredConfiguration] = None
    pingable: Optional[list[PingableConfiguration]] = None

    def disk_usage_report(self) -> dict[str, dict[str, float]]:
        return {str(path): dict(psutil.disk_usage(str(path))._asdict()) for path in self.paths if path.exists()}

    def network_accessibility_report(self) -> dict[str, list[dict[str, str | list[str]]]]:
        if self.pingable is not None:
            return {'network_accessibility': [{'at': str(p.at),
                                               'source': [str(src) for src in p.source]} for p in self.pingable]}
        else:
            return {}

    @staticmethod
    def of(path: Path) -> 'SystemPrincepsConfiguration':
        return SystemPrincepsConfiguration(**from_yaml(path.open('r').read()))

    @staticmethod
    def cpu_ram_info() -> Report:
        return {'hostname': hostname(),
                'core_load': psutil.cpu_percent(interval=0.2, percpu=True),
                'CPU_load': psutil.cpu_percent(interval=0.2, percpu=False),
                'RAM_usage': psutil.virtual_memory().percent}

    def cpu_ram_disk_network_report(self) -> Report:
        return self.cpu_ram_info() | self.disk_usage_report() | self.network_accessibility_report()


@dataclass(frozen=True)
class PrincepsConfiguration:
    exchange: str
    services: ServicePrincepsConfiguration
    system: SystemPrincepsConfiguration

    @staticmethod
    def of(filepath: Path) -> 'PrincepsConfiguration':
        return PrincepsConfiguration(**from_yaml(filepath.open('r').read()))