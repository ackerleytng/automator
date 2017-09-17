"""This test is done using socketpair, which can also be handled by
+ select()
+ send()
+ recv()
"""
import pytest
import sys

from automator.telnet_controller import TelnetController
from automator.responses import Responses

from automator.telnet_shell import TelnetShell


TEST_IP = "192.168.31.131"


@pytest.fixture(scope="module")
def ctrlr():
    s = TelnetShell(TEST_IP)
    return TelnetController("test", s)


def test_login(ctrlr):
    r = Responses([
        ("login: ", "user"),
        ("Password: ", "password"),
    ])

    data = ''.join(ctrlr._recv_handle_lines(responses=r))
    assert "$ " in data


def test_whoami(ctrlr):
    ctrlr.send("whoami")
    data = ''.join(ctrlr._recv_handle_lines())
    assert "user" in data
    assert "$ " in data


def test_sudo(ctrlr):
    r = Responses([
        ("password for user: ", "password"),
    ])

    ctrlr.send("sudo su")
    data = ''.join(ctrlr._recv_handle_lines(responses=r))
    assert "# " in data


def test_whoami_root(ctrlr):
    ctrlr.send("whoami")
    data = ''.join(ctrlr._recv_handle_lines())
    assert "root" in data
    assert "# " in data


def test_exit(ctrlr):
    ctrlr.send("exit")
    data = ''.join(ctrlr._recv_handle_lines())
    assert "$ " in data


def test_ping(ctrlr):
    """This test case is meant to show that the lines can be seen live
    from the remote side.

    To observe the lines appearing, use `pytest -s`
    """
    ctrlr.send("ping -c4 localhost")

    data = []
    for l in ctrlr._recv_handle_lines():
        sys.stdout.write(l)
        data.append(l)

    output = "".join(data)

    assert "icmp_seq=4" in output
    assert "4 packets transmitted" in output
    assert "$ " in output
