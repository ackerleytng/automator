import sys
import telnetlib


class Pipe(object):
    def send(self):
        raise NotImplementedError("Pipe: write has to be implemented!")

    def recv(self):
        raise NotImplementedError("Pipe: write has to be implemented!")


class TelnetPipe(Pipe):
    def __init__(self, host, port=23,
                 user="user", password="password",
                 timeout=5,
                 username_prompt="login: ",
                 password_prompt="Password: ",
                 setup_prompt="$ "):
        """
        username_prompt: string for matching the username prompt
        password_prompt: string for matching the password prompt
        setup_prompt: string for matching the first prompt you'll get
          after the connection is set up
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.timeout = timeout
        self.username_prompt = username_prompt
        self.password_prompt = password_prompt
        self.setup_prompt = setup_prompt

        self.pipe = telnetlib.Telnet(host, port, timeout)

    def send(self, bytes_):
        """Sends bytes_ into the pipe"""
        self.pipe.write(bytes_)

    def recv(self):
        """Reads at least one byte of data unless EOF is hit.
        Returns '' if EOF is hit.
        Blocks if no data is immediately available.
        """
        self.pipe.read_some()

    def build(self):
        """Builds the pipe

        This will do anything necessary to get the pipe up to the first point
          that you can enter a command
        This may involve sending some setup commands as well,
          but we should try and minimize that as much as possible

        Returns all bytes received after setting up the pipe
        """
        encoding = sys.getdefaultencoding()
        self.pipe.read_until(self.username_prompt.encode(encoding))
        self.pipe.write((self.user + "\n").encode(encoding))
        self.pipe.read_until(self.password_prompt.encode(encoding))
        self.pipe.write((self.password + "\n").encode(encoding))

        return self.pipe.read_until(self.setup_prompt.encode(encoding),
                                    self.timeout).decode(encoding)
