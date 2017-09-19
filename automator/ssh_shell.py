import paramiko


from network_shell import NetworkShell


class SshShell(NetworkShell):
    def __init__(self, host, port=22,
                 username="user",
                 password="password"):
        super(SshShell, self).__init__(host, port)

        self.username = username
        self.password = password
        self._shell = None
        self._client = None

    def fileno(self):
        if self._shell is None:
            self.start()

        return self._shell.fileno()

    def start(self, width=1024):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=self.host,
                       username=self.username,
                       password=self.password)
        self._shell = client.invoke_shell(width=width)
        self._client = client

    def stop(self):
        self._client.close()

    def send(self, data):
        self._shell.send(data)

    def recv(self, bytes_to_recv):
        return self._shell.recv(bytes_to_recv)
