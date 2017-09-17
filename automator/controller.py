import select

from responses import Responses


class ControllerException(Exception):
    def __init__(self, msg):
        super(ControllerException, self).__init__(msg)


class Controller(object):
    (LINE, UNKNOWN) = range(2)

    def __init__(self, shell):
        self._shell = shell

        # The buffer for bytes without newline
        self._buffer = ""
        # The buffer for lines
        self._line_buffer = []

    def _recv_into_buffer(self, num, timeout=0.2):
        """Receives at least num characters into self._buffer

        Returns data received if timeout was hit, and None otherwise
        """
        ret = None
        data = ""

        while len(data) < num:
            rl, wl, xl = select.select([self._shell], [], [], timeout)
            if rl:
                d = self._shell.recv(1)
                if d == "":
                    raise IOError("Shell closed")
                else:
                    data += d
            else:
                ret = data
                break

        self._buffer += data

        return ret

    def _recv_lines(self, timeout=0.2):
        ret = None

        # Keep receiving until timeout
        while ret is None:
            ret = self._recv_into_buffer(16, timeout=timeout)

        # Process everything that was received
        lines = self._buffer.split("\n")
        self._buffer = lines.pop()

        self._line_buffer += lines

        # Yield all the lines in the buffer first
        while self._line_buffer:
            yield (Controller.LINE, self._line_buffer.pop(0) + "\n")

        # Yield the leftovers
        yield (Controller.UNKNOWN, self._buffer)

    def _recv_handle_lines(self, responses=Responses([]),
                           tries=32, timeout=0.2,
                           shell_prompts=["$ ", "# ", "] "]):
        """Receives and handles the lines coming in from the remote side.

        responses: a Responses object, allowing you to specify responses
        to possible expected prompts in between shell prompts
        (defaults to no expected prompts/responses)

        shell_prompts: a list of shell prompts that you expect to be seeing.
        (defaults to "$ ", "# " and "] ")

        timeout: the number of seconds to wait before we stop waiting
        for blocks of bytes (16 in this case)
        The higher this value is, the fewer errors you will get,
        but the longer you have to wait for a correct command to
        complete
        (defaults to 0.2 seconds)

        tries: the number of times we are willing to wait for
        a command to complete
        The actual time spent waiting is approximately
        (tries * timeout) seconds.
        (defaults to 32)
        """
        yielded_before = False
        response = None
        max_tries = tries

        while tries > 0:
            for t, data in self._recv_lines(timeout=timeout):
                response = responses.update_response(data, response)

                if t == Controller.LINE:
                    tries = max_tries
                    yielded_before = True
                    yield data
                elif t == Controller.UNKNOWN:
                    # If we see a prompt, we can stop receiving
                    if any([data.endswith(p) for p in shell_prompts]):
                        yielded_before = True
                        yield data

                        # Stop receiving
                        tries = 0
                        break

                    # Try and respond
                    if response is not None:
                        tries = max_tries
                        self.send(response)
                    elif data == "":
                        tries -= 1
                    else:
                        m = ("Can't find appropriate "
                             "response for {}".format(repr(data)))
                        raise ControllerException(m)
                else:
                    m = "Got unknown type {}".format(repr(t))
                    raise ControllerException(m)

        if not yielded_before:
            m = "Didn't receive any lines"
            raise ControllerException(m)

    def send(self, data):
        self._shell.send(data + "\n")

    def send_bytes(self, data):
        self._shell.send(data)
