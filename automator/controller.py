import select
import sys


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

    def _recv_into_buffer(self, num, timeout=1):
        """Receives at least num characters into self._buffer

        Returns data received if timeout was hit, and None otherwise
        """
        ret = None
        data = ""

        while len(data) < num:
            rl, wl, xl = select.select([self._shell], [], [], timeout)
            if rl:
                d = self._shell.recv(1)
                # sys.stdout.write("|{}|".format(repr(d)))
                if d == "":
                    raise IOError("Shell closed")
                else:
                    data += d
            else:
                ret = data
                break

        self._buffer += data

        return ret

    def _recv_lines(self, timeout=1):
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
            yield (Controller.LINE, self._line_buffer.pop() + "\n")

        # Yield the leftovers
        yield (Controller.UNKNOWN, self._buffer)

    def _recv_handle_lines(self, timeout=1, responses=Responses([]),
                           shell_prompts=["$ ", "# ", "] "]):
        yielded_before = False
        response = None
        ok_to_exit = False

        while not ok_to_exit:
            for t, data in self._recv_lines(timeout=timeout):
                response = responses.update_response(data, response)

                if t == Controller.LINE:
                    yielded_before = True
                    yield data
                elif t == Controller.UNKNOWN:
                    # If we see a prompt, we can stop receiving
                    if any([data.endswith(p) for p in shell_prompts]):
                        yielded_before = True
                        yield data

                        # Stop receiving
                        ok_to_exit = True
                        break

                    # Try and respond
                    response = responses.update_response(data, response)
                    if response is not None:
                        self.send(response)
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
        else:
            print "_recv_handle_lines exiting properly"

    def send(self, data):
        self._shell.send(data + "\n")

    def send_bytes(self, data):
        self._shell.send(data)
