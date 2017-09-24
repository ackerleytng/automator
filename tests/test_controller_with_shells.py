import pytest
import sys

from automator.controller import Controller
from automator.responses import Responses

from automator.ssh_shell import SshShell
from automator.telnet_shell import TelnetShell


TEST_IP = "192.168.31.131"


@pytest.fixture(scope="module", params=[SshShell, TelnetShell])
def ctrlr(request):
    s = request.param(TEST_IP)
    c = Controller(s)

    if request.param == TelnetShell:
        c.start(responses=Responses([
            ("login: ", "user"),
            ("Password: ", "password"),
        ]))
    else:
        c.start()

    return c


def test_motd(ctrlr):
    if isinstance(ctrlr, TelnetShell):
        assert "login: user" in ctrlr.motd
    elif isinstance(ctrlr, SshShell):
        assert "login: user" not in ctrlr.motd


def test_whoami(ctrlr):
    ctrlr.send("whoami")
    data = ctrlr.recv()
    print data
    assert "user\r\n" == data
    assert "whoami\n" == ctrlr.sent_data
    assert "$ " in ctrlr.prompt


def test_setup_temp_file(ctrlr):
    r = Responses([
        ("password", "password")
    ])
    ctrlr.send("sudo touch test")
    data = ctrlr.recv(responses=r)
    assert "[sudo] password for user: \r\n" == data


def test_remove_temp_file(ctrlr):
    ctrlr.send("rm test")
    r = Responses([
        ("remove write-protected regular empty file", "yes")
    ])
    data = ctrlr.recv(responses=r)
    assert ("rm: remove write-protected regular "
            "empty file 'test'? yes\r\n") == data


def test_sudo(ctrlr):
    r = Responses([
        ("password for user: ", "password"),
    ])

    ctrlr.send("sudo su")
    data = ctrlr.recv(responses=r)
    # Empty because sudo was previously used,
    #   so no password prompt expected
    assert "" == data


def test_whoami_root(ctrlr):
    ctrlr.send("whoami")
    data = ctrlr.recv()
    assert "root\r\n" == data


def test_exit(ctrlr):
    ctrlr.send("exit")
    data = ctrlr.recv()
    assert "" == data


def test_write_file(ctrlr):
    ctrlr.send("echo 'echo \"enter anything on the "
               "next line to proceed:\"' > test.sh")
    import time
    time.sleep(1)
    data = ctrlr.recv()
    assert "" == data


def test_append_to_file(ctrlr):
    ctrlr.send("echo 'read' >> test.sh")
    data = ctrlr.recv()
    assert "" in data


def test_no_prompt_response(ctrlr):
    ctrlr.send("bash test.sh")
    r = Responses([
        ("", "anything")
    ])
    data = ctrlr.recv(responses=r)
    assert ("enter anything on the next line "
            "to proceed:\r\nanything\r\n") in data


def test_append_more_stuff(ctrlr):
    ctrlr.send("echo 'echo \"enter anything again on the "
               "next line to proceed:\"' >> test.sh")
    data = ctrlr.recv()
    assert "" in data
    ctrlr.send("echo 'read' >> test.sh")
    data = ctrlr.recv()
    assert "" == data


def test_same_response_twice(ctrlr):
    ctrlr.send("bash test.sh")
    r = Responses([
        ("", "anything")
    ])
    data = ctrlr.recv(responses=r)
    assert ("enter anything on the next line to proceed:\r\n"
            "anything\r\n"
            "enter anything again on the next line to proceed:\r\n"
            "anything\r\n") == data


def test_delete_file(ctrlr):
    ctrlr.send("rm test.sh")
    data = ctrlr.recv()
    assert "" == data


def test_ping(ctrlr):
    """This test case is meant to show that the lines can be seen live
    from the remote side.

    To observe the lines appearing, use `pytest -s`
    """
    ctrlr.send("ping -c4 localhost")

    data = []
    for l in ctrlr.recv_live():
        sys.stdout.write(l)
        data.append(l)

    output = "".join(data)

    assert "icmp_seq=4" in output
    assert "4 packets transmitted" in output
