from abc import abstractmethod
from dataclasses import dataclass
from functools import wraps
from itertools import count
from pathlib import Path
from random import randint
from threading import Event, Thread
from time import sleep
from traceback import format_exc
from typing import Callable, Union, Optional, List, Self

from beartype import beartype
from loguru import logger as log
from robotnikmq import RobotnikConfig
from sqlitedict import SqliteDict

from legion_utils.alerter import Alerter
from legion_utils.cli.utils import xdg_data_dir
from legion_utils.core import hostname
from legion_utils.princeps.princeps import (
    ServiceRegistrar,
    TimeDelta,
    DEFAULT_SERVICE_REGISTRY_DIR,
)

DEFAULT_RELAUNCH_DELAY = (
    5  # how many seconds to wait before relaunching a given service
)
DEFAULT_START_DELAY_MAX = (
    5  # by default, start delay is randomized between 0 and this number of seconds
)
DEFAULT_CHECKIN_DELAY = 30  # the delay between when the application checks in
DEFAULT_CHECKIN_INTERVAL = (
    DEFAULT_CHECKIN_DELAY * 2
)  # the time limit for princeps to expect another check-in
DEFAULT_TTL = (
    DEFAULT_CHECKIN_INTERVAL * 2
)  # the time limit for an alert to live based on missed checkins


class Runner(Alerter):
    def __init__(
        self,
        task_id: str,
        exchange: str,
        route: str,
        default_ttl: int,
        start_delay: Union[int, Callable[[], int], None],
        halt_flag: Optional[Event],
        service_registry_dir: Optional[Path],
        check_in_delay: int,
        warn_after_checkin: Optional[TimeDelta],
        error_after_checkin: Optional[TimeDelta],
        critical_after_checkin: Optional[TimeDelta],
        config: Optional[RobotnikConfig] = None,
    ):
        super().__init__(
            task_id=task_id,
            exchange=exchange,
            route=route,
            default_ttl=default_ttl,
            config=config,
        )
        self.halt_flag = halt_flag or Event()
        self.check_in_delay = check_in_delay
        self.start_delay = (
            start_delay
            if start_delay is not None
            else (lambda: randint(0, DEFAULT_START_DELAY_MAX))
        )
        self.registrar = ServiceRegistrar(
            name=self.task_id,
            checkin_interval=self.check_in_delay * 2,
            alert_ttl=default_ttl,
            directory=service_registry_dir,
            warn_after=warn_after_checkin,
            error_after=error_after_checkin,
            critical_after=critical_after_checkin,
        )
        self.start_checkin_thread()

    def start_checkin_thread(self):
        def _run() -> None:
            log.info(f"{self.task_id} - starting Princeps check-in thread...")
            while not self.halt_flag.wait(timeout=self.check_in_delay):
                log.info(f"{self.task_id} - checking in with Princeps")
                self.registrar.check_in()

        thread = Thread(target=_run, daemon=True)
        thread.start()

    @property
    def _start_delay(self) -> int:
        return (
            self.start_delay if not callable(self.start_delay) else self.start_delay()
        )

    def delay_start(self) -> None:
        delay_seconds = abs(self._start_delay)
        log.info(f"Waiting {delay_seconds} seconds before starting...")
        sleep(delay_seconds)

    @abstractmethod
    def __call__(self, func: Callable[[], None]) -> None:
        pass  # pragma: no cover


class Service(Runner):
    def __init__(
        self,
        task_id: str,
        exchange: str,
        route: str,
        ttl: Optional[int] = None,
        start_delay: Union[int, Callable[[], int], None] = None,
        relaunch_delay: int = DEFAULT_RELAUNCH_DELAY,
        jitter: int = 3,
        warn_after_attempts: Optional[int] = None,
        error_after_attempts: Optional[int] = None,
        critical_after_attempts: Optional[int] = None,
        service_registry_dir: Optional[Path] = DEFAULT_SERVICE_REGISTRY_DIR,
        check_in_delay: int = DEFAULT_CHECKIN_DELAY,
        warn_after_checkin: Optional[TimeDelta] = None,
        error_after_checkin: Optional[TimeDelta] = None,
        critical_after_checkin: Optional[TimeDelta] = None,
        halt_flag: Optional[Event] = None,
        config: Optional[RobotnikConfig] = None,
    ):
        super().__init__(
            task_id=task_id,
            exchange=exchange,
            route=route,
            default_ttl=(ttl or DEFAULT_TTL),
            start_delay=start_delay,
            halt_flag=halt_flag,
            service_registry_dir=service_registry_dir,
            check_in_delay=check_in_delay,
            warn_after_checkin=warn_after_checkin,
            error_after_checkin=error_after_checkin,
            critical_after_checkin=critical_after_checkin,
            config=config,
        )
        self.relaunch_delay = relaunch_delay
        self.jitter = jitter
        self.warn_after_attempts = warn_after_attempts or float("inf")
        self.error_after_attempts = error_after_attempts or (
            1 if warn_after_attempts is None else float("inf")
        )
        self.critical_after_attempts = critical_after_attempts or float("inf")

    @property
    def _relaunch_delay(self) -> int:
        return self.relaunch_delay + randint(0 - self.jitter, self.jitter)

    def delay_relaunch(self):
        sleep(abs(self._relaunch_delay))

    def key(self, task_id: str) -> List[str]:
        return [hostname(), "legion", "service_failure", task_id]

    def __call__(self, func: Callable[[], None]) -> Callable[[], None]:
        @wraps(func)
        def retry_infinity_wrapper() -> None:
            last_traceback: Optional[str] = None
            self.delay_start()
            for i in count(1):  # pragma: no branch
                if self.halt_flag.is_set():
                    break
                try:
                    func()
                except Exception as exc:
                    log.exception(exc)
                    last_traceback = format_exc()
                finally:
                    contents = {
                        "task_id": self.task_id,
                        "last_stack_trace": last_traceback,
                        "num_failures": i,
                    }
                    if i == 1:
                        desc = f"Service '{self.task_id}' stopped running"
                    else:
                        desc = f"Service '{self.task_id}' stopped running {i} times in a row"
                    if i >= self.critical_after_attempts:
                        self.broadcast_critical(contents=contents, desc=desc)
                    elif i >= self.error_after_attempts:
                        self.broadcast_error(contents=contents, desc=desc)
                    elif i >= self.warn_after_attempts:
                        self.broadcast_warning(contents=contents, desc=desc)
                    self.delay_relaunch()

        return retry_infinity_wrapper


@beartype
@dataclass(frozen=True)
class TaskSuccess:
    pass


@beartype
@dataclass(frozen=True)
class TaskFailure:
    consecutive_count: int
    desc: str
    contents: dict
    DESC = "Periodic task '{task_id}' failed {num_failures} times in a row"

    @staticmethod
    def content_dict(
        task_id: str, stack_trace: str, num_failures: int
    ) -> dict[str, str]:
        return {
            "task_id": task_id,
            "last_stack_trace": stack_trace,
            "num_failures": num_failures,
        }

    @classmethod
    def of(cls, task_id: str, stack_trace: str) -> Self:
        return TaskFailure(
            0,
            desc=TaskFailure.DESC.format(task_id=task_id, num_failures=0),
            contents=TaskFailure.content_dict(task_id, stack_trace, 0),
        )

    def increment(self, task_id: str, stack_trace: str) -> Self:
        return TaskFailure(
            self.consecutive_count + 1,
            desc=self.DESC.format(
                task_id=task_id, num_failures=self.consecutive_count + 1
            ),
            contents=self.content_dict(
                task_id, stack_trace, self.consecutive_count + 1
            ),
        )


class Periodic(Runner):
    """
    A decorator class which takes a callable, and executes it periodically on a delay (NOT an interval). This class
    keeps track of the results of executions in a local SQLite database and reports on the results every 30 seconds
    automatically in a background daemon thread.
    """

    DEFAULT_DB_NAME = "legion.db"
    DEFAULT_DB_TABLENAME = "legion_periodic_tasks_status"
    REPORTING_DELAY = 30
    TTL = REPORTING_DELAY * 4

    def __init__(
        self,
        task_id: str,
        exchange: str,
        route: str,
        delay: int,
        start_delay: Union[int, Callable[[], int], None] = None,
        relaunch_delay: int = DEFAULT_RELAUNCH_DELAY,
        jitter: Optional[int] = None,
        warn_after_failures: Union[int, float, None] = None,
        error_after_failures: Union[int, float, None] = None,
        critical_after_failures: Union[int, float, None] = None,
        service_registry_dir: Optional[Path] = DEFAULT_SERVICE_REGISTRY_DIR,
        check_in_delay: Optional[int] = None,
        warn_after_checkin: Optional[TimeDelta] = None,
        error_after_checkin: Optional[TimeDelta] = None,
        critical_after_checkin: Optional[TimeDelta] = None,
        halt_flag: Optional[Event] = None,
        config: Optional[RobotnikConfig] = None,
        local_db_path: Path | None = None,
    ):
        super().__init__(
            task_id=task_id,
            exchange=exchange,
            route=route,
            default_ttl=self.TTL,
            start_delay=start_delay,
            halt_flag=halt_flag,
            service_registry_dir=service_registry_dir,
            check_in_delay=(check_in_delay or delay * 2),
            warn_after_checkin=warn_after_checkin,
            error_after_checkin=error_after_checkin,
            critical_after_checkin=critical_after_checkin,
            config=config,
        )
        self.delay = delay
        self.jitter = jitter if jitter is not None else 3
        self.relaunch_delay = relaunch_delay
        self.warn_after_failures = warn_after_failures or float("inf")
        self.error_after_failures = error_after_failures or (
            1 if warn_after_failures is None else float("inf")
        )
        self.critical_after_failures = critical_after_failures or float("inf")
        self._db_path = self._generate_db_path(local_db_path)
        self._reporting_thread = Thread(target=self._report, daemon=True)
        self._reporting_thread.start()

    @staticmethod
    def _generate_db_path(local_db_path: Path | None) -> Path:
        if local_db_path is not None:
            return (
                local_db_path / Periodic.DEFAULT_DB_NAME
                if local_db_path.is_dir()
                else local_db_path
            )
        else:
            return xdg_data_dir() / Periodic.DEFAULT_DB_NAME

    def _db(self) -> SqliteDict:
        return SqliteDict(
            self._db_path, tablename=self.DEFAULT_DB_TABLENAME, autocommit=True
        )

    def get_task_state(self) -> TaskSuccess | TaskFailure | None:
        with self._db() as db:
            return db.get(self.task_id, None)

    def _record_failure(self, last_stack_trace: str) -> TaskFailure:
        with self._db() as db:
            old = db.get(self.task_id, None)
            match old:
                case TaskFailure():
                    new = old.increment(self.task_id, last_stack_trace)
                case _:
                    new = TaskFailure.of(self.task_id, last_stack_trace)
            db[self.task_id] = new
        return new

    def _record_success(self) -> TaskSuccess:
        new = TaskSuccess()
        with self._db() as db:
            db[self.task_id] = new
        return new

    def _report(self):
        while 42:
            sleep(self.REPORTING_DELAY)
            try:
                match result := self.get_task_state():
                    case TaskFailure():
                        log.info(
                            f"Reporting periodic task failure: {self.task_id} - {result.desc}"
                        )
                        if result.consecutive_count >= self.critical_after_failures:
                            self.broadcast_critical(
                                contents=result.contents, desc=result.desc
                            )
                        elif result.consecutive_count >= self.error_after_failures:
                            self.broadcast_error(
                                contents=result.contents, desc=result.desc
                            )
                        elif result.consecutive_count >= self.warn_after_failures:
                            self.broadcast_warning(
                                contents=result.contents, desc=result.desc
                            )
            except Exception as exc:
                log.exception(
                    f"There was an error while attempting to report on a task: {exc}"
                )

    def jittery_delay(self):
        sleep(abs(self.delay + randint(0 - self.jitter, self.jitter)))

    def jittery_error_delay(self):
        sleep(abs(self.relaunch_delay + randint(0 - self.jitter, self.jitter)))

    def key(self, task_id: str) -> List[str]:
        return [hostname(), "legion", "periodic_task_failure", task_id]

    def __call__(self, func: Callable[[], None]) -> Callable[[], None]:
        @wraps(func)
        def run_infinity_wrapper() -> None:
            self.delay_start()
            for _ in count():  # pragma: no branch
                if self.halt_flag.is_set():
                    break
                try:
                    func()
                    self._record_success()
                    self.jittery_delay()
                except Exception as exc:
                    log.exception(
                        f"An handled error occurred while running the task: {exc}"
                    )
                    self._record_failure(last_stack_trace=format_exc())
                    self.jittery_error_delay()

        return run_infinity_wrapper
