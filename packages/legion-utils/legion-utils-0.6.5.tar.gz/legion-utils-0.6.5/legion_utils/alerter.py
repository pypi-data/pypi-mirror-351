from abc import abstractmethod, ABC
from typing import Optional, Any

from robotnikmq import RobotnikConfig

from legion_utils import WarningMsg, broadcast_alert_msg, ErrorMsg, CriticalMsg


class Alerter(ABC):
    def __init__(self,
                 task_id: str,
                 exchange: str,
                 route: str,
                 default_ttl: int,
                 config: Optional[RobotnikConfig] = None):
        self.task_id = task_id
        self.exchange = exchange
        self.route = route
        self.config = config
        self.default_ttl = default_ttl

    @abstractmethod
    def key(self, task_id: str) -> list[str]:
        pass  # pragma: no cover

    def broadcast_warning(self, contents: dict[str, Any],
                          desc: str,
                          ttl: Optional[int] = None) -> None:
        broadcast_alert_msg(exchange=self.exchange,
                            route=self.route,
                            config=self.config,
                            alert=WarningMsg(contents=contents,
                                             key=self.key(self.task_id),
                                             desc=desc,
                                             ttl=(ttl or self.default_ttl)))

    def broadcast_error(self, contents: dict[str, Any],
                        desc: str,
                        ttl: Optional[int] = None) -> None:
        broadcast_alert_msg(exchange=self.exchange,
                            route=self.route,
                            config=self.config,
                            alert=ErrorMsg(contents=contents,
                                           key=self.key(self.task_id),
                                           desc=desc,
                                           ttl=(ttl or self.default_ttl)))

    def broadcast_critical(self, contents: dict[str, Any],
                           desc: str,
                           ttl: Optional[int] = None) -> None:
        broadcast_alert_msg(exchange=self.exchange,
                            route=self.route,
                            config=self.config,
                            alert=CriticalMsg(contents=contents,
                                              key=self.key(self.task_id),
                                              desc=desc,
                                              ttl=(ttl or self.default_ttl)))
