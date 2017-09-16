"""This test is done using socketpair, which can also be handled by
+ select()
+ send()
+ recv()
"""
import pytest
import socket
import time
from automator import telnet_controller
from automator import timeout
import multiprocessing
import sys


def print_and_send(pipe, d):
    print "Sending |{}|".format(repr(d))
    pipe.send(d)


def _tester_0(pipe):
    print_and_send(pipe, "some line\n")

    time.sleep(5)

    print_and_send(pipe, "some other line\n")


def _testee_0(controller):
    with pytest.raises(timeout.Timeout) as e:
        print "Receiving with timeout of 3 seconds"
        controller._recv_into_buffer(12, 3)

    assert "some line\n" in e.value.message
    assert "some line\n" in controller._buffer
    assert [] == controller._line_buffer

    print "Testee just waiting to end"
    time.sleep(3)


def _tester_1(pipe):
    print_and_send(pipe, "12345678")


def _testee_1(controller):
    d = controller._recv_into_buffer(4, 3)
    assert d is None
    assert "1234" == controller._buffer
    assert [] == controller._line_buffer


# Just keep specifying testers and testees above testees

def get_params():
    current_module = sys.modules[__name__]
    num_testers = len([f for f in dir(current_module)
                       if f.startswith("_tester")])

    # Used [::-1] to reverse the order of test cases so that
    #   the latest test case that I add will be the first to
    #   get tested (more likely to be the one I'm interested in)
    return ([(getattr(current_module, "_tester_{}".format(i)),
             getattr(current_module, "_testee_{}".format(i)))
            for i in range(num_testers)][::-1],
            ["test_pair_{}".format(i) for i in range(num_testers)][::-1])


params, ids = get_params()


@pytest.mark.parametrize("tester, testee", params, ids=ids)
def test__recv_into_buffer(tester, testee):
    parent_end, child_end = socket.socketpair()

    def wrapper():
        parent_end.close()
        c = telnet_controller.TelnetController("test", child_end)

        testee(c)

        child_end.close()

    p = multiprocessing.Process(target=wrapper)
    p.start()

    child_end.close()
    tester(parent_end)
    parent_end.close()

    p.join()
