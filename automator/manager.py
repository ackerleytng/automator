import automator.pipe as pipe
import sys


class PipeManager(object):
    def send(self):
        raise NotImplementedError("Pipe: write has to be implemented!")

    def recv(self):
        raise NotImplementedError("Pipe: write has to be implemented!")


class NetworkPipeManager(PipeManager):
    """Documentation for NetworkPipeManager

    """
    def __init__(self, host, port=23,
                 user="user", password="password",
                 timeout=5,
                 username_prompt="login: ", password_prompt="Password: "):
        super(NetworkPipeManager, self).__init__()
        self.pipe = pipe.TelnetPipe(host, port, user, password, timeout)

        # Retain the last line of setup_data as shell_prompt
        setup_data = self.pipe.build()
        self.shell_prompt = setup_data.split('\n')[-1]

    def send_bytes(self, bytes_):
        """Sends raw bytes into the pipe"""
        self.pipe.send(bytes_)

    def send_keystrokes(self, string, encoding=sys.getdefaultencoding()):
        """Sends keystrokes into the pipe, will do encoding for you"""
        self.send_bytes(string.encode(encoding))

    def send(self, string, encoding=sys.getdefaultencoding()):
        """Sends keystrokes into the pipe, and presses Enter!
        Will do encoding for you.

        Use this to send a command, like

        ```
        telnet_pipe_manager.send("ls")
        ```
        """
        self.send_keystrokes(string + "\n")

    def recv_bytes(self):
        """Receives raw bytes from the pipe.
        Returns '' if EOF is hit.
        Blocks if no data is immediately available.
        """
        return self.pipe.recv()

    def recv(self, encoding=sys.getdefaultencoding()):
        return self.recv_bytes().decode(encoding)
