from threading import Event

from legion_utils import Service, Periodic


def test_basic_service(mocker, tmp_path):
    mocker.patch("legion_utils.core.broadcast")
    (tmp_path / 'registry').mkdir()
    halt_flag = Event()
    first_round_done = Event()
    second_round_done = Event()

    @Service("test_service_func",
             "test",
             "test.basic.service",
             start_delay=0,
             relaunch_delay=0,
             halt_flag=halt_flag,
             jitter=0,
             error_after_attempts=2,
             service_registry_dir=tmp_path / 'registry')
    def test_service_func():
        if not first_round_done.is_set():
            first_round_done.set()
        elif not second_round_done.is_set():
            second_round_done.set()
        else:
            halt_flag.set()

    test_service_func()
    assert first_round_done.is_set()
    assert second_round_done.is_set()
    assert halt_flag.is_set()


def test_basic_service_critical(mocker, tmp_path):
    mocker.patch("legion_utils.core.broadcast")
    (tmp_path / 'registry').mkdir()
    halt_flag = Event()

    @Service("test_service_func",
             "test",
             "test.basic.service.critical",
             relaunch_delay=0,
             halt_flag=halt_flag,
             jitter=0,
             critical_after_attempts=1,
             service_registry_dir=tmp_path / 'registry')
    def test_service_func():
        halt_flag.set()

    test_service_func()
    assert halt_flag.is_set()


def test_basic_service_warning(mocker, tmp_path):
    mocker.patch("legion_utils.core.broadcast")
    (tmp_path / 'registry').mkdir()
    halt_flag = Event()

    @Service("test_service_func",
             "test",
             "test.basic.service.warning",
             start_delay=0,
             relaunch_delay=0,
             halt_flag=halt_flag,
             jitter=0,
             warn_after_attempts=1,
             service_registry_dir=tmp_path / 'registry')
    def test_service_func():
        halt_flag.set()

    test_service_func()
    assert halt_flag.is_set()


def test_basic_service_exception(mocker, tmp_path):
    mocker.patch("legion_utils.core.broadcast")
    (tmp_path / 'registry').mkdir()
    halt_flag = Event()

    @Service("test_service_func",
             "test",
             "test.basic.service.exception",
             start_delay=0,
             relaunch_delay=0,
             halt_flag=halt_flag,
             jitter=0,
             service_registry_dir=tmp_path / 'registry')
    def test_service_func():
        halt_flag.set()
        raise RuntimeError("Shit happens")

    test_service_func()
    assert halt_flag.is_set()


def test_basic_periodic(mocker, tmp_path):
    mocker.patch("legion_utils.core.broadcast")
    (tmp_path / 'registry').mkdir()
    halt_flag = Event()
    first_round_done = Event()
    second_round_done = Event()

    @Periodic("test_periodic_func",
              "test",
              "test.basic.periodic",
              delay=0,
              halt_flag=halt_flag,
              jitter=0,
              error_after_failures=2,
              service_registry_dir=tmp_path / 'registry')
    def test_service_func():
        if not first_round_done.is_set():
            first_round_done.set()
        elif not second_round_done.is_set():
            second_round_done.set()
        else:
            halt_flag.set()

    test_service_func()
    assert first_round_done.is_set()
    assert second_round_done.is_set()
    assert halt_flag.is_set()


def test_periodic_exception(mocker, tmp_path):
    mocker.patch("legion_utils.core.broadcast")
    (tmp_path / 'registry').mkdir()
    halt_flag = Event()
    first_round_done = Event()

    @Periodic("test_periodic_func",
              "test",
              "test.basic.periodic",
              delay=0,
              halt_flag=halt_flag,
              jitter=0,
              error_after_failures=2,
              service_registry_dir=tmp_path / 'registry')
    def test_service_func():
        if not first_round_done.is_set():
            first_round_done.set()
        else:
            halt_flag.set()
        raise RuntimeError("Shit happens")

    test_service_func()
    assert halt_flag.is_set()


def test_periodic_warning(mocker, tmp_path):
    mocker.patch("legion_utils.core.broadcast")
    (tmp_path / 'registry').mkdir()
    halt_flag = Event()
    first_round_done = Event()

    @Periodic("test_periodic_func",
              "test",
              "test.basic.periodic.warning",
              delay=0,
              halt_flag=halt_flag,
              jitter=0,
              warn_after_failures=2,
              service_registry_dir=tmp_path / 'registry')
    def test_service_func():
        if not first_round_done.is_set():
            first_round_done.set()
        else:
            halt_flag.set()
        raise RuntimeError("Shit happens")

    test_service_func()
    assert halt_flag.is_set()


def test_periodic_critical(mocker, tmp_path):
    mocker.patch("legion_utils.core.broadcast")
    (tmp_path / 'registry').mkdir()
    halt_flag = Event()
    first_round_done = Event()

    @Periodic("test_periodic_func",
              "test",
              "test.basic.periodic.critical",
              delay=0,
              halt_flag=halt_flag,
              jitter=0,
              critical_after_failures=2,
              service_registry_dir=tmp_path / 'registry')
    def test_service_func():
        if not first_round_done.is_set():
            first_round_done.set()
        else:
            halt_flag.set()
        raise RuntimeError("Shit happens")

    test_service_func()
    assert halt_flag.is_set()
