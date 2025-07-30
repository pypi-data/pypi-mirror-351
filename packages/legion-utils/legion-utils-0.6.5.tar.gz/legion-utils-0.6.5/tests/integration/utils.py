from contextlib import contextmanager
from multiprocessing import Process, Event
from os.path import realpath
from pathlib import Path
from re import compile as regex
from subprocess import check_output
from time import sleep
from typing import Callable, Any, Tuple, Optional

from pytest import mark
from robotnikmq.config import server_config, RobotnikConfig
from robotnikmq.core import Message
from robotnikmq.subscriber import Subscriber, ExchangeBinding
from typeguard import typechecked


from robotnikmq import RobotnikConfig


# VAGRANT_VM_NAME = "legion-utils-vm"
# VAGRANT_RUNNING_PAT = regex(VAGRANT_VM_NAME + r"\s+running \(libvirt\)")
# VAGRANT_CWD = Path(realpath(__file__)).parent.parent.parent

# HERE = Path(realpath(__file__)).parent
# CA_CERT = HERE / "vagrant" / "pki" / "robotnik-ca.crt"
# USERNAME = "legion"
# PASSWORD = "hackme"
# VIRTUAL_HOST = "/legion"
# CERT = HERE / "vagrant" / "pki" / "issued" / "legion-utils-vm" / "legion-utils-vm.crt"
# KEY = HERE / "vagrant" / "pki" / "issued" / "legion-utils-vm" / "legion-utils-vm.key"
# PORT = 5671
# LOCALHOST = "127.0.0.1"

# CONFIG = RobotnikConfig(
#     tiers=[
#         [
#             server_config(
#                 LOCALHOST, PORT, USERNAME, PASSWORD, VIRTUAL_HOST, CA_CERT, CERT, KEY
#             )
#         ]
#     ]
# )


# @contextmanager
# def sub_process(
#     target: Callable,
#     args: Optional[Tuple[Any, ...]] = None,
#     name: Optional[str] = None,
#     terminate: bool = True,
# ):
#     proc = Process(target=target, args=args or (), name=name)
#     proc.start()
#     try:
#         sleep(0.2)
#         yield proc
#     finally:
#         if terminate:
#             proc.terminate()
#         proc.join()


# @typechecked
# def vagrant_up() -> bool:
#     return bool(
#         VAGRANT_RUNNING_PAT.search(
#             check_output(
#                 ["vagrant", "status", VAGRANT_VM_NAME], cwd=VAGRANT_CWD
#             ).decode()
#         )
#     )


# vagrant_test = mark.skipif(not vagrant_up(), reason="rabbitmq-vm needs to be running")


@contextmanager
def does_not_raise():
    yield
