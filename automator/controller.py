import select
import sys


from responses import Responses


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
            ret = self._recv_into_buffer(16, timeout)

        # Process everything that was received
        lines = self._buffer.split("\n")
        self._buffer = lines.pop()

        self._line_buffer += lines

        # Yield all the lines in the buffer first
        while self._line_buffer:
            yield (Controller.LINE, self._line_buffer.pop() + "\n")

        # Yield the leftovers
        yield (Controller.UNKNOWN, self._buffer)

    def _recv_handle_lines(self, responses=Responses([])):
        response = None

        for t, data in self._recv_lines:
            response = responses.update_response(data, response)

            if t == Controller.LINE:
                yield data
            elif t == Controller.UNKNOWN:
                response = responses.update_response(data, response)
                if response is not None:
                    self._shell.send(response + "\n")
