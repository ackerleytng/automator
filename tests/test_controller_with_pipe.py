"""This test is done using socketpair, which can also be handled by
+ select()
+ send()
+ recv()
"""
import pytest
import socket
import time
import multiprocessing
import sys

from automator.controller import Controller as C
from automator.controller import ControllerException
from automator.responses import Responses


def helper_three_diff_responses(pipe):
    print_and_send(pipe, "please send the required words:\n")

    required_list = ["red\n", "yellow\n", "blue\n"]

    i = 0
    while i < len(required_list):
        required = required_list[i]
        check = pipe.recv(len(required))
        print "Expected |{}|, got |{}|".format(repr(required), repr(check))
        if check == required:
            i += 1
        else:
            return

    print_and_send(pipe, "thanks\n")

    print_and_send(pipe, "$ ")

    # Hold the pipe open for 1.1 seconds
    #   because we will be using a timeout of 1
    # timeout should only happen after the first 2 lines have been received
    #   (on the iteration that returns (C.UNKNOWN, ""))
    time.sleep(1.1)


def test_three_diff_responses(controller):
    r = Responses([
        ("", "red"),
        ("", "yellow"),
        ("", "blue")
    ])
    for i, (_, l) in enumerate(controller._recv_handle_lines(responses=r)):
        print "Received |{}|".format(repr(l))
        if i == 0:
            assert ("please send the required words:\n") == l
        elif i == 1:
            assert ("thanks\n") == l
        else:
            assert ("$ ") == l


def helper_diff_response_same_empty_prompt(pipe):
    check = ""
    while check != "moo":
        print_and_send(pipe, "please send 'moo':\n")
        check = pipe.recv(3)
    print_and_send(pipe, "thanks\n")

    check = ""
    while check != "meow":
        print_and_send(pipe, "please send 'meow' this time:\n")
        check = pipe.recv(4)
    print_and_send(pipe, "thanks\n")

    print_and_send(pipe, "# ")

    # Hold the pipe open for 1.1 seconds
    #   because we will be using a timeout of 1
    # timeout should only happen after the first 2 lines have been received
    #   (on the iteration that returns (C.UNKNOWN, ""))
    time.sleep(1.1)


def test_diff_response_same_empty_prompt(controller):
    r = Responses([
        ("", "moo"),
        ("", "meow")
    ])
    for i, (_, l) in enumerate(controller._recv_handle_lines(responses=r)):
        print "Received |{}|".format(repr(l))
        if i == 0:
            # "moo\n" does not appear in this line because the pipe
            #   that we're using isn't like a shell that echos back
            assert ("please send 'moo':\n") == l
        elif i == 1:
            assert ("thanks\n") == l


def helper_recv_response(pipe):
    print_and_send(pipe, "please send 'moo' to continue: ")

    if "moo" == pipe.recv(3):
        print_and_send(pipe, "thanks\n")
        print_and_send(pipe, "# ")

    # Hold the pipe open for 1.1 seconds
    #   because we will be using a timeout of 1
    # timeout should only happen after the first 2 lines have been received
    #   (on the iteration that returns (C.UNKNOWN, ""))
    time.sleep(1.1)


def test_recv_response(controller):
    r = Responses([
        ("continue: ", "moo")
    ])
    for i, (_, l) in enumerate(controller._recv_handle_lines(responses=r)):
        print "Received |{}|".format(repr(l))
        if i == 0:
            # "moo\n" does not appear in this line because the pipe
            #   that we're using isn't like a shell that echos back
            assert ("please send 'moo' to continue: thanks\n") == l
        elif i == 1:
            assert ("# ") == l

    assert i == 1


def helper_recv(pipe):
    for i in range(2):
        print_and_send(pipe, "a" * 16 + "\n")

    print_and_send(pipe, "b")

    # Hold the pipe open for longer
    #   because we will be using a timeout of 1
    # timeout should only happen after the first 2 lines have been received
    #   (on the iteration that returns (C.UNKNOWN, ""))
    time.sleep(2)


def test_recv_lines(controller):
    with pytest.raises(ControllerException) as e:
        for i, (_, l) in enumerate(controller._recv_handle_lines()):
            print "Received |{}|".format(repr(l))
            if i < 2:
                assert ("a" * 16 + "\n") == l

    assert e.value.message == "Can't find appropriate response for 'b'"


def print_and_send(pipe, d):
    print "Sending |{}|".format(repr(d))
    pipe.send(d)


def helper_pipe_closed(pipe):
    print_and_send(pipe, "a")


def test_pipe_closed(controller):
    with pytest.raises(IOError) as e:
        controller._recv_into_buffer(2)

    assert e.value.message == "Shell closed"


def helper_recv_lines(pipe):
    for i in range(2):
        print_and_send(pipe, "a" * 16 + "\n")

    # Hold the pipe open for 1.1 seconds
    #   because we will be using a timeout of 1
    # timeout should only happen after the first 2 lines have been received
    #   (on the iteration that returns (C.UNKNOWN, ""))
    time.sleep(1.1)


def test_recv_lines(controller):
    for i, r in enumerate(controller._recv_lines()):
        if i < 2:
            assert (C.LINE, "a" * 16 + "\n") == r
        elif i == 2:
            assert (C.UNKNOWN, "") == r

    assert i == 2


def helper_recv_less_than_sent(pipe):
    print_and_send(pipe, "12345678")
    # Receiving should be fast enough, no need to hold open


def test_recv_less_than_sent(controller):
    d = controller._recv_into_buffer(4, 3)
    assert d is None
    assert "1234" == controller._buffer
    assert [] == controller._line_buffer


def helper_recv_1_more_than_sent_hold_pipe_open(pipe):
    print_and_send(pipe, "aaaa")

    # Hold pipe open so that timeout will be hit
    time.sleep(5.1)


def test_recv_1_more_than_sent_hold_pipe_open(controller):
    assert controller._recv_into_buffer(5, timeout=5) == "aaaa"


def helper_exact(pipe):
    print_and_send(pipe, "aaaa")


def test_exact(controller):
    # If there is no timeout, don't return anything
    assert controller._recv_into_buffer(4) is None
    assert controller._buffer == "aaaa"


def helper_recv_with_delay(pipe):
    print_and_send(pipe, "some line\n")

    time.sleep(5)

    print_and_send(pipe, "some other line\n")


def test_recv_with_delay(controller):
    print "Receiving with timeout of 3 seconds"
    d = controller._recv_into_buffer(12, 3)

    assert d == "some line\n"
    assert "some line\n" in controller._buffer
    assert [] == controller._line_buffer

    print "Testee just waiting to end"
    time.sleep(3)


@pytest.fixture
def controller(request):
    test_name = request.node.name
    helper_name = test_name.replace("test", "helper")
    current_module = sys.modules[__name__]
    helper = getattr(current_module, helper_name)

    sending_end, recving_end = socket.socketpair()

    # To make it look nicer if -s flag is used for pytest
    print

    def wrapper():
        recving_end.close()

        helper(sending_end)

        sending_end.close()

    p = multiprocessing.Process(target=wrapper)
    p.start()

    sending_end.close()
    yield C(recving_end)
    recving_end.close()

    p.join()
