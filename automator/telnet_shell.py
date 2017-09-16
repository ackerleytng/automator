import telnetlib

from network_shell import NetworkShell


class TelnetShell(NetworkShell):
    def __init__(self, host, port=23,
                 username="user",
                 password="password",
                 timeout=5):
        super(TelnetShell, self).__init__(host, port)

        self.username = username
        self.password = password
        self.timeout = timeout
        self._shell = None

    def fileno(self):
        if self._shell is None:
            self.start()

        return self._shell.fileno()

    def start(self):
        self._shell = telnetlib.Telnet(self.host, self.port,
                                       self.timeout)

    def stop(self):
        self._shell.close()

    def send(self, data):
        self._shell.write(data)

    def recv(self, bytes_to_recv):
        # bytes_to_recv is ignored since telnetlib doesn't need it
        return self._shell.read_some()
