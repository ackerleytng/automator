import select

from responses import Responses


class ControllerException(Exception):
    def __init__(self, msg):
        super(ControllerException, self).__init__(msg)


class Controller(object):
    (LINE, UNKNOWN, PROMPT) = range(3)

    def __init__(self, shell):
        self._shell = shell

        # The buffer for bytes without newline
        self._buffer = ""
        # The buffer for lines
        self._line_buffer = []

        # This is string data that needs to be removed
        #   from data received
        self.sent_data = ""

        # Sent data is echoed twice. I don't completely understand this.
        #   Meanwhile, I will remove it exactly twice
        self._sent_data_rm_count = 2

        # This is the last prompt displayed on the remote side
        #   e.g. "user@telnetd:~$" or
        #   after `sudo su`, "user@telnetd:~#"
        self.prompt = ""

    def start(self, responses=Responses([]),
              tries=32, timeout=0.2,
              shell_prompts=["$ ", "# ", "] ", ">"]):
        self.motd = self.recv(responses=responses,
                              tries=tries,
                              timeout=timeout,
                              shell_prompts=shell_prompts) \
                        .replace(self.prompt, "", 1)
        return self

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
                           shell_prompts=["$ ", "# ", "] ", ">"]):
        """Receives and handles the lines coming in from the remote side.
        Yields lines as they come in.

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
        instance = None
        max_tries = tries

        self._line_buffer = []

        while tries > 0:
            for t, data in self._recv_lines(timeout=timeout):
                response, instance = responses.update_response(data, response)

                if t == Controller.LINE:
                    tries = max_tries
                    yielded_before = True
                    yield t, data
                elif t == Controller.UNKNOWN:
                    # If we see a prompt, we can stop receiving
                    if any([data.endswith(p) for p in shell_prompts]):
                        yielded_before = True
                        yield Controller.PROMPT, data

                        # Stop receiving
                        tries = 0
                        break

                    # Try and respond
                    if response is not None:
                        tries = max_tries
                        self._shell.send(response + "\n")
                        responses.use(instance)
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

    def recv_live(self, responses=Responses([]),
                  tries=32, timeout=0.2,
                  shell_prompts=["$ ", "# ", "] ", ">"]):
        """Handles parsing of full responses (_recv_handle_lines handles
        responding to intermediate prompts within commands)

        recv_live will take note of the prompt and sent command and
        only yield the command's responses line by line
        """

        for t, data in self._recv_handle_lines(responses=responses,
                                               tries=tries,
                                               timeout=timeout,
                                               shell_prompts=shell_prompts):
            if t == Controller.LINE:
                if self.prompt != "" and self.prompt in data:
                    data = data.replace(self.prompt, "", 1)

                # Undo the effect of shell echoing
                #   Chose not to simply turn off echoing because we want
                #   to keep the side being controlled as unmodified as possible
                #   Also, I'm not sure if echo can be turned off
                #     on Windows' cmd
                # We match on the rstripped version because even though we send
                #   \n, unices seem to reply with \r\n, and
                #   Windows' cmd replies with the original \n
                while (self._sent_data_rm_count > 0 and
                       self.sent_data.rstrip() in data):
                    rn_version = self.sent_data.replace("\n", "\r\n")
                    if rn_version in data:
                        data = data.replace(rn_version, "", 1)
                        self._sent_data_rm_count -= 1
                    elif self.sent_data in data:
                        data = data.replace(self.sent_data, "", 1)
                        self._sent_data_rm_count -= 1

                if data != "":
                    yield data
            elif t == Controller.PROMPT:
                self.prompt = data
            else:
                m = "Got unknown type {}".format(repr(t))
                raise ControllerException(m)

    def recv(self, responses=Responses([]),
             tries=32, timeout=0.2,
             shell_prompts=["$ ", "# ", "] ", ">"]):
        return "".join(self.recv_live(responses=responses,
                                      tries=tries,
                                      timeout=timeout,
                                      shell_prompts=shell_prompts))

    def send(self, data):
        self.send_bytes(data + "\n")

    def send_bytes(self, data):
        self.sent_data = data
        self._sent_data_rm_count = 2

        self._shell.send(data)
