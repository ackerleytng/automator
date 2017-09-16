import select


from timeout import Timeout


class Controller(object):
    def __init__(self, shell):
        self._shell = shell

        # The buffer for bytes without newline
        self._buffer = ""
        # The buffer for lines
        self._line_buffer = []

    def _recv_into_buffer(self, num, timeout):
        """Receives at least num characters into self._buffer
        Raises Timeout if time is up and num has not been reached
        """
        data = ""

        while len(data) < num:
            rl, wl, xl = select.select([self._shell], [], [], timeout)
            if rl:
                data += self._shell.recv(1)
            else:
                break

        self._buffer += data

        if len(data) < num:
            raise Timeout(data)

    def _update_buffers(self):
        lines = self._buffer.split("\n")
        self._buffer = lines.pop()

        self._line_buffer += lines

    def _read_line(self):
        """Reads and returns the first series of bytes ending with \n

        All lines after that will be placed into self._line_buffer,
        all bytes after the last newline will be placed into self._buffer
        """
        if len(self._line_buffer) > 0:
            return self._line_buffer.pop(0)

        while "\n" not in self._buffer:
            self._update_buffers()
            if len(self._line_buffer) > 0:
                return self._line_buffer.pop(0)
            else:
                raise Timeout(self._buffer)

            #def _handle(self):
