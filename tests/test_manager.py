import pytest
import automator.manager as manager


@pytest.fixture
def network_pipe_manager():
    return manager.NetworkPipeManager("192.168.237.132")


def test_setup(network_pipe_manager):
    assert "$" in network_pipe_manager.shell_prompt
