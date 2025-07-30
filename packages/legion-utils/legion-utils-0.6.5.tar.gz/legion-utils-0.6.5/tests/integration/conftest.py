# pylint: disable=redefined-outer-name
from pytest import fixture
from testcontainers.rabbitmq import RabbitMqContainer

from robotnikmq import RobotnikConfig


RABBITMQ_VERSION = "3.11.2"


@fixture(scope="session")
def rabbitmq():
    with RabbitMqContainer(f"rabbitmq:{RABBITMQ_VERSION}") as rabbitmq:
        yield rabbitmq


@fixture
def robotnikmq_config(rabbitmq):
    yield RobotnikConfig.from_connection_params(rabbitmq.get_connection_params())
