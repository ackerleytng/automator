import pytest
import sys

from automator.controller import Controller
from automator.responses import Responses

from automator.ssh_shell import SshShell


TEST_IP = "192.168.31.131"


@pytest.fixture(scope="module")
def ctrlr():
    s = SshShell(TEST_IP)
    return Controller(s)


def test_get_motd(ctrlr):
    # Calling _recv_handle_lines also causes python to
    #   access fileno(), which triggers SshShell.start()
    data = ''.join(ctrlr._recv_handle_lines())
    assert "$ " in data


def test_whoami(ctrlr):
    ctrlr.send("whoami")
    data = ''.join(ctrlr._recv_handle_lines())
    assert "user" in data
    assert "$ " in data


def test_setup_temp_file(ctrlr):
    r = Responses([
        ("password", "password")
    ])
    ctrlr.send("sudo touch test")
    data = "".join(ctrlr._recv_handle_lines(responses=r))
    assert "sudo touch test" in data
    assert "password" in data
    assert "$ " in data


def test_remove_temp_file(ctrlr):
    ctrlr.send("rm test")
    r = Responses([
        ("remove write-protected regular empty file", "yes")
    ])
    data = "".join(ctrlr._recv_handle_lines(responses=r))
    assert "yes" in data
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


def test_write_file(ctrlr):
    ctrlr.send("echo 'echo \"enter anything on the "
               "next line to proceed:\"' > test.sh")
    data = ''.join(ctrlr._recv_handle_lines())
    assert "$ " in data


def test_append_to_file(ctrlr):
    ctrlr.send("echo 'read' >> test.sh")
    data = ''.join(ctrlr._recv_handle_lines())
    assert "$ " in data


def test_no_prompt_response(ctrlr):
    ctrlr.send("bash test.sh")
    r = Responses([
        ("", "anything")
    ])
    data = ''.join(ctrlr._recv_handle_lines(responses=r))
    assert "$ " in data


def test_append_more_stuff(ctrlr):
    ctrlr.send("echo 'echo \"enter anything again on the "
               "next line to proceed:\"' >> test.sh")
    data = ''.join(ctrlr._recv_handle_lines())
    assert "$ " in data
    ctrlr.send("echo 'read' >> test.sh")
    data = ''.join(ctrlr._recv_handle_lines())
    assert "$ " in data


def test_same_response_twice(ctrlr):
    ctrlr.send("bash test.sh")
    r = Responses([
        ("", "anything")
    ])
    data = ''.join(ctrlr._recv_handle_lines(responses=r))
    assert len(data.split("anything\r\n")) == 3
    assert "$ " in data


def test_delete_file(ctrlr):
    ctrlr.send("rm test.sh")
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
