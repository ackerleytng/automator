import abc


class Shell(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def fileno(self):
        """Providing fileno so that this can be used with select.select()
        """
        pass

    @abc.abstractmethod
    def start(self):
        """Starts up this shell
        """
        pass

    @abc.abstractmethod
    def stop(self):
        """Cleans up and stops this shell
        """
        pass

    @abc.abstractmethod
    def send(self, data):
        """Sends data, as is, to the shell"""
        pass

    @abc.abstractmethod
    def recv(self, bytes_to_recv):
        """Receives bytes_to_recv from the shell"""
        pass
