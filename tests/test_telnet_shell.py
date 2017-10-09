import select
import pytest

from pynomator import telnet_shell

# Not sure how to do this other than to hard code this ip
TEST_IP = "192.168.31.131"


def _read_until(selectable, until):
    data = ""

    while until not in data:
        rl, wl, xl = select.select([selectable], [], [], 0.0)
        for c in rl:
            d = c.recv(1)
            data += d

    return data


@pytest.fixture(scope="module")
def shell():
    return telnet_shell.TelnetShell(TEST_IP)


def test_getting_login_prompt(shell):
    data = _read_until(shell, "login: ")
    assert "telnetd" in data


def test_entering_username(shell):
    shell.send("user\n")
    data = _read_until(shell, "Password: ")
    assert "Password: " in data


def test_entering_password(shell):
    shell.send("password\n")
    data = _read_until(shell, "$ ")
    assert "$ " in data


def test_stop(shell):
    shell.stop()
