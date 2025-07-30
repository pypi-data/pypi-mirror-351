from socket import gethostname

from pytest import mark, raises
from robotnikmq import Message

from legion_utils import NotificationMsg, AlertMsg, Priority, InfoMsg, ActivityMsg
from legion_utils import (
    WarningMsg,
    ErrorMsg,
    CriticalMsg,
    priority_of,
)
from legion_utils import valid_priority

from tests.integration.utils import does_not_raise

try:
    from pytest_cov.embed import cleanup_on_sigterm
except ImportError:
    pass
else:
    cleanup_on_sigterm()


HOSTNAME = gethostname()


@mark.parametrize(
    "candidate, exp_priority, expectation",
    [
        ("warning", Priority.WARNING, does_not_raise()),
        ("error", Priority.ERROR, does_not_raise()),
        ("critical", Priority.CRITICAL, does_not_raise()),
        ("activity", Priority.ACTIVITY, does_not_raise()),
        ("information", Priority.INFO, does_not_raise()),
        ("warn", Priority.WARNING, does_not_raise()),
        ("err", Priority.ERROR, does_not_raise()),
        ("crit", Priority.CRITICAL, does_not_raise()),
        ("info", Priority.INFO, does_not_raise()),
        ("w", Priority.WARNING, does_not_raise()),
        ("e", Priority.ERROR, does_not_raise()),
        ("c", Priority.CRITICAL, does_not_raise()),
        ("a", Priority.ACTIVITY, does_not_raise()),
        ("i", Priority.INFO, does_not_raise()),
        ("not a priority", None, raises(ValueError)),
        (2, Priority.WARNING, does_not_raise()),
        (3, Priority.ERROR, does_not_raise()),
        (4, Priority.CRITICAL, does_not_raise()),
        (1, Priority.ACTIVITY, does_not_raise()),
        (0, Priority.INFO, does_not_raise()),
        (5, None, raises(ValueError)),
        (-1, None, raises(ValueError)),
        (Priority.WARNING, Priority.WARNING, does_not_raise()),
        (Priority.ERROR, Priority.ERROR, does_not_raise()),
        (Priority.CRITICAL, Priority.CRITICAL, does_not_raise()),
        (Priority.ACTIVITY, Priority.ACTIVITY, does_not_raise()),
        (Priority.INFO, Priority.INFO, does_not_raise()),
    ],
)
def test_priority_of(candidate, exp_priority, expectation):
    with expectation:
        assert priority_of(candidate) == exp_priority


@mark.parametrize(
    "candidate, exp",
    [
        ("warning", True),
        ("error", True),
        ("critical", True),
        ("activity", True),
        ("information", True),
        ("warn", True),
        ("err", True),
        ("crit", True),
        ("info", True),
        ("w", True),
        ("e", True),
        ("c", True),
        ("a", True),
        ("i", True),
        ("not a priority", False),
        (2, True),
        (3, True),
        (4, True),
        (1, True),
        (0, True),
        (5, False),
        (-1, False),
        (None, False),
        (Priority.INFO, True),
        (Priority.ACTIVITY, True),
        (Priority.WARNING, True),
        (Priority.ERROR, True),
        (Priority.CRITICAL, True),
    ],
)
def test_valid_priority(candidate, exp):
    assert valid_priority(candidate) == exp


@mark.parametrize(
    "contents,key,desc,ttl,prio,exp_contents,exp_key,exp_desc,exp_ttl,exp_prio,expectation",
    [
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            ["a", "b", "c"],
            "stuff",
            30,
            Priority.INFO,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            Priority.INFO,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            "abc",
            "stuff",
            30,
            Priority.INFO,
            {"stuff": "something", "msg_src": HOSTNAME},
            "abc",
            "stuff",
            30,
            Priority.INFO,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            None,
            None,
            None,
            None,
            {"stuff": "something", "msg_src": HOSTNAME},
            None,
            None,
            None,
            Priority.INFO,
            does_not_raise(),
        ),
    ],
)
def test_notification_msg(
    contents,
    key,
    desc,
    ttl,
    prio,
    exp_contents,
    exp_key,
    exp_desc,
    exp_ttl,
    exp_prio,
    expectation,
):
    with expectation:
        notification = NotificationMsg(contents, key, desc, ttl, prio)
        assert notification.contents == exp_contents
        assert notification.priority == exp_prio
        assert notification.ttl == exp_ttl
        assert notification.alert_key == exp_key
        assert notification.desc == exp_desc
        assert notification.msg_src == HOSTNAME


@mark.parametrize(
    "contents,ttl,exp_contents,exp_ttl,exp_prio,expectation",
    [
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            30,
            {"stuff": "something", "msg_src": HOSTNAME},
            30,
            Priority.INFO,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            30,
            {"stuff": "something", "msg_src": HOSTNAME},
            30,
            Priority.INFO,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            None,
            {"stuff": "something", "msg_src": HOSTNAME},
            None,
            Priority.INFO,
            does_not_raise(),
        ),
    ],
)
def test_info_msg(contents, ttl, exp_contents, exp_ttl, exp_prio, expectation):
    with expectation:
        msg = InfoMsg(contents, ttl)
        assert msg.contents == exp_contents
        assert msg.priority == exp_prio
        assert msg.ttl == exp_ttl
        assert msg.alert_key is None
        assert msg.desc is None
        assert msg.msg_src == HOSTNAME


@mark.parametrize(
    "contents,ttl,exp_contents,exp_ttl,exp_prio,expectation",
    [
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            30,
            {"stuff": "something", "msg_src": HOSTNAME},
            30,
            Priority.ACTIVITY,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            30,
            {"stuff": "something", "msg_src": HOSTNAME},
            30,
            Priority.ACTIVITY,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            None,
            {"stuff": "something", "msg_src": HOSTNAME},
            None,
            Priority.ACTIVITY,
            does_not_raise(),
        ),
    ],
)
def test_activity_msg(contents, ttl, exp_contents, exp_ttl, exp_prio, expectation):
    with expectation:
        msg = ActivityMsg(contents, ttl)
        assert msg.contents == exp_contents
        assert msg.priority == exp_prio
        assert msg.ttl == exp_ttl
        assert msg.alert_key is None
        assert msg.desc is None
        assert msg.msg_src == HOSTNAME


@mark.parametrize(
    "contents,key,desc,ttl,prio,exp_contents,exp_key,exp_desc,exp_ttl,exp_prio,expectation",
    [
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            ["a", "b", "c"],
            "stuff",
            30,
            Priority.WARNING,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            Priority.WARNING,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            "abc",
            "stuff",
            30,
            Priority.WARNING,
            {"stuff": "something", "msg_src": HOSTNAME},
            "abc",
            "stuff",
            30,
            Priority.WARNING,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            ["a", "b", "c"],
            "stuff",
            None,
            None,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            Priority.WARNING,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            ["a", "b", "c"],
            "stuff",
            None,
            Priority.INFO,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            Priority.WARNING,
            raises(ValueError),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            "",
            "stuff",
            None,
            Priority.CRITICAL,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            Priority.CRITICAL,
            raises(ValueError),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            ["a", "b", "c"],
            "",
            None,
            Priority.CRITICAL,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            Priority.CRITICAL,
            raises(ValueError),
        ),
    ],
)
def test_alert_msg(
    contents,
    key,
    desc,
    ttl,
    prio,
    exp_contents,
    exp_key,
    exp_desc,
    exp_ttl,
    exp_prio,
    expectation,
):
    with expectation:
        alert = AlertMsg(contents, key, desc, ttl, prio)
        assert alert.contents == exp_contents
        assert alert.priority == exp_prio
        assert alert.ttl == exp_ttl
        assert alert.key == exp_key
        assert alert.description == exp_desc
        assert alert.msg_src == HOSTNAME


def test_alert_msg_of():
    msg = Message.of(
        {
            "alert_key": "[stuff]",
            "ttl": 60,
            "description": "Testing stuff",
            "priority": Priority.ERROR,
            "stuff": "stuff",
        }
    )
    alert = AlertMsg.of(msg)
    assert alert.contents["stuff"] == "stuff"


def test_alert_msg_of_no_key():
    msg = Message.of(
        {
            "ttl": 60,
            "description": "Testing stuff",
            "priority": Priority.ERROR,
            "stuff": "stuff",
        }
    )
    with raises(ValueError):
        AlertMsg.of(msg)
        assert False


def test_alert_msg_of_no_description():
    msg = Message.of(
        {
            "alert_key": "[stuff]",
            "ttl": 60,
            "priority": Priority.ERROR,
            "stuff": "stuff",
        }
    )
    with raises(ValueError):
        AlertMsg.of(msg)
        assert False


def test_alert_msg_of_no_priority():
    msg = Message.of(
        {
            "alert_key": "[stuff]",
            "ttl": 60,
            "description": "Testing stuff",
            "stuff": "stuff",
        }
    )
    with raises(ValueError):
        AlertMsg.of(msg)
        assert False


def test_alert_msg_of_no_ttl():
    msg = Message.of(
        {
            "alert_key": "[stuff]",
            "description": "Testing stuff",
            "priority": Priority.ERROR,
            "stuff": "stuff",
        }
    )
    with raises(ValueError):
        AlertMsg.of(msg)
        assert False


def test_alert_msg_of_invalid_priority():
    msg = Message.of(
        {
            "alert_key": "[stuff]",
            "ttl": 60,
            "description": "Testing stuff",
            "priority": "Priority.ERROR",
            "stuff": "stuff",
        }
    )
    with raises(ValueError):
        AlertMsg.of(msg)
        assert False


def test_alert_msg_of_int_priority():
    msg = Message.of(
        {
            "alert_key": "[stuff]",
            "ttl": 60,
            "description": "Testing stuff",
            "priority": 3,
            "stuff": "stuff",
        }
    )
    alert = AlertMsg.of(msg)
    assert alert.contents["stuff"] == "stuff"
    assert alert.priority == Priority.ERROR


def test_alert_msg_of_invalid_ttl():
    msg = Message.of(
        {
            "alert_key": "[stuff]",
            "ttl": "27",
            "description": "Testing stuff",
            "priority": Priority.ERROR,
            "stuff": "stuff",
        }
    )
    with raises(ValueError):
        AlertMsg.of(msg)
        assert False


def test_alert_msg_of_negative_ttl():
    msg = Message.of(
        {
            "alert_key": "[stuff]",
            "ttl": -1,
            "description": "Testing stuff",
            "priority": Priority.ERROR,
            "stuff": "stuff",
        }
    )
    with raises(ValueError):
        AlertMsg.of(msg)
        assert False


@mark.parametrize(
    "contents,key,desc,ttl,exp_contents,exp_key,exp_desc,exp_ttl,expectation",
    [
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            ["a", "b", "c"],
            "stuff",
            30,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            "abc",
            "stuff",
            30,
            {"stuff": "something", "msg_src": HOSTNAME},
            "abc",
            "stuff",
            30,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            ["a", "b", "c"],
            "stuff",
            None,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            "",
            "stuff",
            None,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            raises(ValueError),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            ["a", "b", "c"],
            "",
            None,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            raises(ValueError),
        ),
    ],
)
def test_warning_msg(
    contents, key, desc, ttl, exp_contents, exp_key, exp_desc, exp_ttl, expectation
):
    with expectation:
        alert = WarningMsg(contents, key, desc, ttl)
        assert alert.contents == exp_contents
        assert alert.priority == Priority.WARNING
        assert alert.ttl == exp_ttl
        assert alert.key == exp_key
        assert alert.description == exp_desc
        assert alert.msg_src == HOSTNAME


@mark.parametrize(
    "contents,key,desc,ttl,exp_contents,exp_key,exp_desc,exp_ttl,expectation",
    [
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            ["a", "b", "c"],
            "stuff",
            30,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            "abc",
            "stuff",
            30,
            {"stuff": "something", "msg_src": HOSTNAME},
            "abc",
            "stuff",
            30,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            ["a", "b", "c"],
            "stuff",
            None,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            "",
            "stuff",
            None,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            raises(ValueError),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            ["a", "b", "c"],
            "",
            None,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            raises(ValueError),
        ),
    ],
)
def test_error_msg(
    contents, key, desc, ttl, exp_contents, exp_key, exp_desc, exp_ttl, expectation
):
    with expectation:
        alert = ErrorMsg(contents, key, desc, ttl)
        assert alert.contents == exp_contents
        assert alert.priority == Priority.ERROR
        assert alert.ttl == exp_ttl
        assert alert.key == exp_key
        assert alert.description == exp_desc
        assert alert.msg_src == HOSTNAME


@mark.parametrize(
    "contents,key,desc,ttl,exp_contents,exp_key,exp_desc,exp_ttl,expectation",
    [
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            ["a", "b", "c"],
            "stuff",
            30,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            "abc",
            "stuff",
            30,
            {"stuff": "something", "msg_src": HOSTNAME},
            "abc",
            "stuff",
            30,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            ["a", "b", "c"],
            "stuff",
            None,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            does_not_raise(),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            "",
            "stuff",
            None,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            raises(ValueError),
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            ["a", "b", "c"],
            "",
            None,
            {"stuff": "something", "msg_src": HOSTNAME},
            "[a][b][c]",
            "stuff",
            30,
            raises(ValueError),
        ),
    ],
)
def test_critical_msg(
    contents, key, desc, ttl, exp_contents, exp_key, exp_desc, exp_ttl, expectation
):
    with expectation:
        alert = CriticalMsg(contents, key, desc, ttl)
        assert alert.contents == exp_contents
        assert alert.priority == Priority.CRITICAL
        assert alert.ttl == exp_ttl
        assert alert.key == exp_key
        assert alert.description == exp_desc
        assert alert.msg_src == HOSTNAME


@mark.parametrize(
    "contents1,key1,desc1,ttl1,prio1,contents2,key2,desc2,ttl2,prio2,k_eq,d_eq,t_eq,p_eq,k_m,d_m",
    [
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            ["a", "b", "c"],
            "stuff",
            30,
            Priority.WARNING,
            {"stuff": "something", "msg_src": HOSTNAME},
            ["a", "b", "c"],
            "stuff",
            30,
            Priority.WARNING,
            True,
            True,
            True,
            True,
            False,
            True,
        ),
        (
            {"stuff": "something", "msg_src": HOSTNAME},
            ["a", "b", "c"],
            "stuff",
            30,
            Priority.WARNING,
            {"stuff": "something1", "msg_src": HOSTNAME},
            ["a1", "b1", "c1"],
            "stu1ff",
            31,
            Priority.ERROR,
            False,
            False,
            False,
            False,
            False,
            False,
        ),
    ],
)
def test_alert_comparison(
    contents1,
    key1,
    desc1,
    ttl1,
    prio1,
    contents2,
    key2,
    desc2,
    ttl2,
    prio2,
    k_eq,
    d_eq,
    t_eq,
    p_eq,
    k_m,
    d_m,
):
    alert1 = AlertMsg(contents1, key1, desc1, ttl1, prio1)
    alert2 = AlertMsg(contents2, key2, desc2, ttl2, prio2)
    cmp = alert1.compare(alert2)
    assert cmp.key_equal == k_eq
    assert cmp.desc_equal == d_eq
    assert cmp.ttl_equal == t_eq
    assert cmp.priority_equal == p_eq
    assert cmp.key_match == k_m
    assert cmp.desc_match == d_m
