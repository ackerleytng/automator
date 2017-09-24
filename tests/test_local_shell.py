import select
import pytest

from automator import local_shell


def _read_until(selectable, until):
    data = ""

    while until not in data:
        rl, wl, xl = select.select([selectable], [], [], 10)
        for c in rl:
            d = c.recv(1)
            data += d

    return data


@pytest.fixture(scope="module")
def shell():
    return local_shell.LocalShell()


def test_getting_login_prompt(shell):
    data = _read_until(shell, "$ ")
    assert "$ " in data


def test_ls(shell):
    shell.send("ls -al\n")
    data = _read_until(shell, "$ ")
    print data
    assert "README.md" in data
    assert "tests" in data
    assert "automator" in data
    assert "$ " in data


def test_stop(shell):
    shell.stop()
