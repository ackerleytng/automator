import pytest
import sys

from automator.controller import Controller

from automator.ssh_shell import SshShell


TEST_IP = "192.168.31.132"


@pytest.fixture(scope="module")
def ctrlr():
    s = SshShell(TEST_IP)
    return Controller(s)


def test_login(ctrlr):
    data = ''.join(ctrlr.recv())
    assert ">" in data


def test_ipconfig(ctrlr):
    ctrlr.send("ipconfig")
    data = ''.join(ctrlr.recv())
    assert "Windows IP Configuration" in data
    assert TEST_IP in data
    assert ">" in data


def test_ping(ctrlr):
    """This test case is meant to show that the lines can be seen live
    from the remote side.

    To observe the lines appearing, use `pytest -s`
    """
    ctrlr.send("ping -n 4 127.0.0.1")

    data = []
    for l in ctrlr.recv():
        sys.stdout.write(l)
        data.append(l)

    output = "".join(data)

    assert "Sent = 4" in output
    assert "TTL=128" in output
    assert ">" in output
