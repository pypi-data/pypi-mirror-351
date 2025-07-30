from multiprocessing import Process, Event
from pprint import pprint
from time import sleep
from typing import Callable

from robotnikmq import RobotnikConfig, Subscriber, ExchangeBinding
from typeguard import typechecked

from legion_utils import broadcast, Priority, broadcast_info, broadcast_activity
from legion_utils import (
    broadcast_alert,
    broadcast_warning,
    broadcast_error,
    broadcast_critical,
    NotificationMsg,
    broadcast_alert_msg,
    ErrorMsg,
)

META_QUEUE = "skynet.legion"
RABBITMQ_VERSION = "3.11.2"

try:
    from pytest_cov.embed import cleanup_on_sigterm
    cleanup_on_sigterm()
except ImportError:
    pass


@typechecked
def broadcast_receive(config: RobotnikConfig, pub: Callable, sub: Callable):
    msg_received = Event()

    def subscriber():
        for msg in Subscriber(
            [ExchangeBinding(META_QUEUE, "#")],
            config=config,
        ).consume():
            sub(msg)
            msg_received.set()

    sub_proc = Process(target=subscriber)
    sub_proc.start()
    sleep(0.2)
    pub_proc = Process(target=pub)
    pub_proc.start()
    assert msg_received.wait(timeout=5)
    pub_proc.terminate()
    sub_proc.terminate()
    pub_proc.join()
    sub_proc.join()


def test_basic_broadcast_receive(robotnikmq_config):
    def pub():
        NotificationMsg(
            contents={"stuff": "Hello world!"}, priority=Priority.ACTIVITY, ttl=3
        ).broadcast(META_QUEUE, "test", robotnikmq_config)

    def sub(msg):
        pprint(msg)

    broadcast_receive(robotnikmq_config, pub, sub)


def test_basic_broadcast_alert(robotnikmq_config):
    def pub():
        alert = ErrorMsg(
            contents={"stuff": "Hello world!"}, key="stuff", desc="stuff", ttl=3
        )
        broadcast_alert_msg(META_QUEUE, "test", alert, robotnikmq_config)

    def sub(msg):
        pprint(msg)

    broadcast_receive(robotnikmq_config, pub, sub)


def test_basic_broadcast_and_receive(robotnikmq_config):
    def pub():
        broadcast(
            META_QUEUE,
            route="legion-utils-vm.test",
            ttl=3,
            priority=Priority.ACTIVITY,
            contents={"stuff": "Hello world!"},
            config=robotnikmq_config,
        )

    def sub(msg):
        pprint(msg)

    broadcast_receive(robotnikmq_config, pub, sub)


def test_broadcast_info(robotnikmq_config):
    def pub():
        broadcast_info(
            META_QUEUE,
            route="legion-utils-vm.test",
            contents={"stuff": "Hello world!"},
            config=robotnikmq_config,
        )

    def sub(msg):
        assert "ttl" not in msg.contents
        assert msg.contents["priority"] == 0
        assert msg.routing_key == "legion-utils-vm.test.info"

    broadcast_receive(robotnikmq_config, pub, sub)


def test_broadcast_activity(robotnikmq_config):
    def pub():
        broadcast_activity(
            META_QUEUE,
            route="legion-utils-vm.test",
            contents={"stuff": "Hello world!"},
            config=robotnikmq_config,
        )

    def sub(msg):
        assert "ttl" not in msg.contents
        assert msg.contents["priority"] == 1
        assert msg.routing_key == "legion-utils-vm.test.activity"

    broadcast_receive(robotnikmq_config, pub, sub)


def test_broadcast_alert(robotnikmq_config):
    def pub():
        broadcast_alert(
            META_QUEUE,
            route="legion-utils-vm.test",
            description="Testing stuff",
            alert_key="legion-utils-vm.test",
            contents={"stuff": "Hello world!"},
            config=robotnikmq_config,
        )

    def sub(msg):
        assert msg.contents["ttl"] == 30
        assert msg.contents["priority"] == 2
        assert msg.routing_key == "legion-utils-vm.test.warning"

    broadcast_receive(robotnikmq_config, pub, sub)


def test_broadcast_warning(robotnikmq_config):
    def pub():
        broadcast_warning(
            META_QUEUE,
            route="legion-utils-vm.test",
            desc="Testing stuff",
            alert_key="legion-utils-vm.test",
            contents={"stuff": "Hello world!"},
            config=robotnikmq_config,
        )

    def sub(msg):
        assert msg.contents["ttl"] == 30
        assert msg.contents["priority"] == 2
        assert msg.routing_key == "legion-utils-vm.test.warning"

    broadcast_receive(robotnikmq_config, pub, sub)


def test_broadcast_error(robotnikmq_config):
    def pub():
        broadcast_error(
            META_QUEUE,
            route="legion-utils-vm.test",
            desc="Testing stuff",
            alert_key="legion-utils-vm.test",
            contents={"stuff": "Hello world!"},
            config=robotnikmq_config,
        )

    def sub(msg):
        assert msg.contents["ttl"] == 30
        assert msg.contents["priority"] == 3
        assert msg.routing_key == "legion-utils-vm.test.error"

    broadcast_receive(robotnikmq_config, pub, sub)


def test_broadcast_critical(robotnikmq_config):
    def pub():
        broadcast_critical(
            META_QUEUE,
            route="legion-utils-vm.test",
            desc="Testing stuff",
            alert_key="legion-utils-vm.test",
            contents={"stuff": "Hello world!"},
            config=robotnikmq_config,
        )

    def sub(msg):
        assert msg.contents["ttl"] == 30
        assert msg.contents["priority"] == 4
        assert msg.routing_key == "legion-utils-vm.test.critical"

    broadcast_receive(robotnikmq_config, pub, sub)
