import pytest
import sys

from pynomator.controller import Controller

from pynomator.ssh_shell import SshShell


TEST_IP = "192.168.31.180"


@pytest.fixture(scope="module")
def ctrlr():
    s = SshShell(TEST_IP)
    return Controller(s).start()


def test_login(ctrlr):
    assert "Microsoft Windows" in ctrlr.motd


def test_ipconfig(ctrlr):
    ctrlr.send("ipconfig")
    data = ctrlr.recv()
    assert "Windows IP Configuration" in data
    assert TEST_IP in data


def test_ping(ctrlr):
    """This test case is meant to show that the lines can be seen live
    from the remote side.

    To observe the lines appearing, use `pytest -s`
    """
    ctrlr.send("ping -n 4 127.0.0.1")

    data = []
    for l in ctrlr.recv_live():
        sys.stdout.write(l)
        data.append(l)

    output = "".join(data)

    assert "Sent = 4" in output
    assert "TTL=128" in output
