from enum import IntEnum
from functools import cache
from pprint import pformat
from re import match
from socket import gethostname
from typing import Dict, Any, Optional, Union, List

from robotnikmq import Topic, Message, RobotnikConfig, log
from typeguard import typechecked


@cache
def hostname() -> str:
    return gethostname().lower()


@typechecked
class Priority(IntEnum):
    INFO = 0
    ACTIVITY = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


INFO = {"info", "information", "i"}
ACTIVITY = {"activity", "a"}
WARNING = {"warning", "warn", "w"}
ERROR = {"error", "err", "e"}
CRITICAL = {"critical", "crit", "c"}


@typechecked
def valid_priority(candidate: Any) -> bool:
    if isinstance(candidate, Priority):
        return True
    if isinstance(candidate, str):
        return any(
            candidate.lower() in P for P in [INFO, ACTIVITY, WARNING, ERROR, CRITICAL]
        )
    if isinstance(candidate, int):
        return any(candidate == i for i in Priority)
    return False


@typechecked
def priority_of(candidate: Union[str, int]) -> Priority:
    if isinstance(candidate, str):
        if candidate.lower() in INFO:
            return Priority.INFO
        if candidate.lower() in ACTIVITY:
            return Priority.ACTIVITY
        if candidate.lower() in WARNING:
            return Priority.WARNING
        if candidate.lower() in ERROR:
            return Priority.ERROR
        if candidate.lower() in CRITICAL:
            return Priority.CRITICAL
    if isinstance(candidate, int):
        return Priority(candidate)
    raise ValueError(f'"{candidate}" cannot be mapped to a valid priority')


class NotificationMsg:
    """This is the default message type from which all other types inherit. It
       has the most basic and essential properties of a Legion message. Most of
       the properties are Optional because they're not necessary for a message
       type of "Notification". You probably should not be using this type
       directly without setting the priorities and TTLs that you want.
    """
    @typechecked
    def __init__(
        self,
        contents: Dict[str, Any],
        alert_key: Union[str, List[str], None] = None,
        desc: Optional[str] = None,
        ttl: Optional[int] = None,
        priority: Optional[Priority] = None,
    ):
        default_contents: Dict[str, Any] = {'msg_src': hostname()}
        self.contents = {**default_contents, **contents}
        self.alert_key = (
            "[" + "][".join(alert_key) + "]"
            if isinstance(alert_key, List)
            else alert_key
        )
        self.desc = desc
        self.ttl = ttl
        self.priority = priority or Priority.INFO

    @property
    def msg_src(self) -> Optional[str]:
        """Returns the value of the msg_src property, which is typically the
           hostname of the machine that generated the message, however, this
           value can be overridden by settings it in the contents dict.

        Returns:
            Optional[str]: returns the string stored in contents['msg_src'] if
                           its present in the contents dict or None if its not.
        """
        return self.contents.get('msg_src')

    @typechecked
    def broadcast(
        self, exchange: str, route: str, config: Optional[RobotnikConfig] = None
    ) -> None:
        """Broadcasts the message to a given exchange and route, with an
           optional Robotnik configuration which can be used to broadcast the
           message to a wholly different set of servers than the one that would
           normally be used by the RobotnikMQ library.

        Args:
            exchange (str): The topic exchange to broadcast to. See:
                            https://www.rabbitmq.com/tutorials/amqp-concepts.html#exchanges
            route (str): The routing key for the message. See:
                         https://www.rabbitmq.com/tutorials/tutorial-four-python.html
            config (Optional[RobotnikConfig], optional): An optional configuration that can be used
                                                         to publish the message to a completely
                                                         different set of RabbitMQ servers than what
                                                         would otherwise be used by RobotnikMQ by
                                                         default. Defaults to None.
        """
        broadcast_msg(exchange, route, self, config)


@typechecked
class InfoMsg(NotificationMsg):
    def __init__(self, contents: Dict[str, Any], ttl: Optional[int] = None):
        super().__init__(contents=contents, ttl=ttl, priority=Priority.INFO)


@typechecked
class ActivityMsg(NotificationMsg):
    def __init__(self, contents: Dict[str, Any], ttl: Optional[int] = None):
        super().__init__(contents=contents, ttl=ttl, priority=Priority.ACTIVITY)


class AlertComparison:
    @typechecked
    def __init__(self, first: "AlertMsg", second: "AlertMsg"):
        self.key = first.key, second.key
        self.desc = first.desc, second.desc
        self.ttl = first.ttl, second.ttl
        self.priority = first.priority, second.priority
        self.contents = first.contents, second.contents

    @property
    def key_equal(self) -> bool:
        return self.key[0] == self.key[1]

    @property
    def desc_equal(self) -> bool:
        return self.desc[0] == self.desc[1]

    @property
    def ttl_equal(self) -> bool:
        return self.ttl[0] == self.ttl[1]

    @property
    def priority_equal(self) -> bool:
        return self.priority[0] == self.priority[1]

    @property
    def key_match(self) -> bool:
        return bool(match(*self.key) or match(self.key[1], self.key[0]))

    @property
    def desc_match(self) -> bool:
        return bool(match(*self.desc) or match(self.desc[1], self.desc[0]))


def alert_key_str(key: Union[str, list[str]]) -> str:
    return "[" + "][".join(key) + "]" if isinstance(key, List) else key


class AlertMsg(NotificationMsg):
    @typechecked
    def __init__(
        self,
        contents: Dict[str, Any],
        key: Union[str, List[str]],
        desc: str,
        ttl: Optional[int] = None,
        priority: Optional[Priority] = None,
        from_msg: Optional[Message] = None,
    ):
        if priority is not None and priority < Priority.WARNING:
            raise ValueError("Alerts can only have a priority of WARNING (2) or higher")
        if not desc:
            raise ValueError("Alerts have to have a description")
        if not key:
            raise ValueError("Alerts have to have a key")
        super().__init__(
            desc=desc,
            priority=priority or Priority.WARNING,
            ttl=ttl or 30,
            contents=contents,
        )
        self.alert_key = alert_key_str(key)
        self.msg = from_msg

    @typechecked
    def compare(self, other: "AlertMsg") -> AlertComparison:
        return AlertComparison(self, other)

    @property
    def key(self) -> str:
        return self.alert_key

    @property
    def description(self) -> Optional[str]:
        return self.desc

    @staticmethod
    def of(msg: Message) -> "AlertMsg":  # pylint: disable=C0103
        if "ttl" not in msg.contents:
            raise ValueError(
                f"Message id {msg.msg_id} cannot be interpreted as an alert "
                f"as it does not have a TTL: {pformat(msg.to_dict())}"
            )
        if "priority" not in msg.contents:
            raise ValueError(
                f"Message id {msg.msg_id} cannot be interpreted as an alert "
                f"as it does not have a priority: {pformat(msg.to_dict())}"
            )
        if not valid_priority(msg.contents["priority"]):
            raise ValueError(
                f"Message id {msg.msg_id} cannot be interpreted as an alert "
                f"as it does not have a valid priority: {pformat(msg.to_dict())}"
            )
        if not isinstance(msg.contents["ttl"], int) or msg.contents["ttl"] < 0:
            raise ValueError(
                f"Message id {msg.msg_id} cannot be interpreted as an alert "
                f"as it does not have a valid TTL: {pformat(msg.to_dict())}"
            )
        if "alert_key" not in msg.contents:
            raise ValueError(
                f"Message id {msg.msg_id} cannot be interpreted as an alert "
                f"as it does not have an alert key: {pformat(msg.to_dict())}"
            )
        if "description" not in msg.contents:
            raise ValueError(
                f"Message id {msg.msg_id} cannot be interpreted as an alert "
                f"as it does not have a description: {pformat(msg.to_dict())}"
            )
        return AlertMsg(
            msg.contents,
            key=msg.contents["alert_key"],
            desc=msg.contents["description"],
            ttl=msg.contents["ttl"],
            priority=priority_of(msg.contents["priority"]),
            from_msg=msg,
        )


class WarningMsg(AlertMsg):
    @typechecked
    def __init__(
        self,
        contents: Dict[str, Any],
        key: Union[str, List[str]],
        desc: str,
        ttl: Optional[int] = None,
    ):
        if not desc:
            raise ValueError("Warnings (alerts) have to have a description")
        if not key:
            raise ValueError("Warnings (alerts) have to have a key")
        super().__init__(
            key=key,
            desc=desc,
            priority=Priority.WARNING,
            ttl=ttl or 30,
            contents=contents,
        )


class ErrorMsg(AlertMsg):
    @typechecked
    def __init__(
        self,
        contents: Dict[str, Any],
        key: Union[str, List[str]],
        desc: str,
        ttl: Optional[int] = None,
    ):
        if not desc:
            raise ValueError("Errors (alerts) have to have a description")
        if not key:
            raise ValueError("Errors (alerts) have to have a key")
        super().__init__(
            key=key,
            desc=desc,
            priority=Priority.ERROR,
            ttl=ttl or 30,
            contents=contents,
        )


class CriticalMsg(AlertMsg):
    @typechecked
    def __init__(
        self,
        contents: Dict[str, Any],
        key: Union[str, List[str]],
        desc: str,
        ttl: Optional[int] = None,
    ):
        if not desc:
            raise ValueError("Critical Alerts have to have a description")
        if not key:
            raise ValueError("Critical Alerts have to have a key")
        super().__init__(
            key=key,
            desc=desc,
            priority=Priority.CRITICAL,
            ttl=ttl or 30,
            contents=contents,
        )


@typechecked
def broadcast_msg(
    exchange: str,
    route: str,
    notification: NotificationMsg,
    config: Optional[RobotnikConfig] = None,
) -> None:
    broadcast(
        exchange=exchange,
        route=route,
        priority=notification.priority,
        contents=notification.contents,
        ttl=notification.ttl,
        description=notification.desc,
        alert_key=notification.alert_key,
        config=config,
    )


@typechecked
def broadcast_alert_msg(
    exchange: str, route: str, alert: AlertMsg, config: Optional[RobotnikConfig] = None
) -> None:
    broadcast(
        exchange=exchange,
        route=route,
        priority=alert.priority,
        contents=alert.contents,
        ttl=alert.ttl,
        description=alert.desc,
        alert_key=alert.alert_key,
        config=config,
    )


@typechecked
def broadcast(
    exchange: str,
    route: str,
    priority: Priority,
    contents: Dict[str, Any],
    ttl: Optional[int] = None,
    description: Optional[str] = None,
    alert_key: Optional[str] = None,
    config: Optional[RobotnikConfig] = None,
):
    _contents: Dict[str, Any] = {"priority": priority.value}
    if priority.value >= 2:
        assert (
            description is not None
        ), "Alerts (e.g. WARNING, ERROR, CRITICAL) must have a description"
        assert (
            ttl is not None
        ), "Alerts (e.g. WARNING, ERROR, CRITICAL) must have a ttl (to clear an alert, set the ttl to 0)"
        assert (
            alert_key is not None
        ), "Alerts (e.g. WARNING, ERROR, CRITICAL) must have an alert_key"
    if ttl is not None:
        _contents["ttl"] = ttl
    if description is not None:
        _contents["description"] = description
    if alert_key is not None:
        _contents["alert_key"] = alert_key
    _contents.update(contents)
    route += f".{priority.name.lower()}"
    Topic(exchange=exchange, config=config).broadcast(
        Message.of(contents=_contents), routing_key=route
    )


@typechecked
def broadcast_info(
    exchange: str,
    route: str,
    contents: Dict[str, Any],
    config: Optional[RobotnikConfig] = None,
):
    # broadcast(exchange, route, priority=Priority.INFO, contents=contents, config=config)
    NotificationMsg(contents=contents).broadcast(exchange=exchange, route=route, config=config)


@typechecked
def broadcast_activity(
    exchange: str,
    route: str,
    contents: Dict[str, Any],
    config: Optional[RobotnikConfig] = None,
):
    broadcast(
        exchange, route, priority=Priority.ACTIVITY, contents=contents, config=config
    )


@typechecked
def broadcast_alert(
    exchange: str,
    route: str,
    description: str,
    alert_key: str,
    contents: Dict[str, Any],
    ttl: int = 30,
    priority: Priority = Priority.WARNING,
    config: Optional[RobotnikConfig] = None,
) -> None:
    broadcast(
        exchange,
        route,
        ttl=ttl,
        priority=priority,
        contents=contents,
        config=config,
        description=description,
        alert_key=alert_key,
    )


@typechecked
def broadcast_warning(
    exchange: str,
    route: str,
    desc: str,
    alert_key: str,
    contents: Dict[str, Any],
    ttl: int = 30,
    config: Optional[RobotnikConfig] = None,
):
    broadcast_alert(
        exchange,
        route,
        description=desc,
        alert_key=alert_key,
        contents=contents,
        ttl=ttl,
        priority=Priority.WARNING,
        config=config,
    )


@typechecked
def broadcast_error(
    exchange: str,
    route: str,
    desc: str,
    alert_key: str,
    contents: Dict[str, Any],
    ttl: int = 30,
    config: Optional[RobotnikConfig] = None,
):
    broadcast_alert(
        exchange,
        route,
        description=desc,
        alert_key=alert_key,
        contents=contents,
        ttl=ttl,
        priority=Priority.ERROR,
        config=config,
    )


@typechecked
def broadcast_critical(
    exchange: str,
    route: str,
    desc: str,
    alert_key: str,
    contents: Dict[str, Any],
    ttl: int = 30,
    config: Optional[RobotnikConfig] = None,
):
    broadcast_alert(
        exchange,
        route,
        description=desc,
        alert_key=alert_key,
        contents=contents,
        ttl=ttl,
        priority=Priority.CRITICAL,
        config=config,
    )
