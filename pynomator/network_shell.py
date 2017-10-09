import abc

from shell import Shell


class NetworkShell(Shell):
    __metaclass__ = abc.ABCMeta

    def __init__(self, host, port):
        self._host = host
        self._port = port

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port
