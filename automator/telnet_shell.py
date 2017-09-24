import struct
import telnetlib
from telnetlib import DO, DONT, IAC, WILL, WONT, NAWS, SB, SE


from network_shell import NetworkShell


def build_callback(width):
    # From https://stackoverflow.com/questions/38288887/python-telnetlib-read-until-returns-cut-off-string
    def set_max_window_size(tsocket, command, option):
        """
        Set Window size to resolve line width issue
        Set Windows size command: IAC SB NAWS <16-bit value>
                                  <16-bit value> IAC SE
        --> inform the Telnet server of the window width and height.
        Refer to https://www.ietf.org/rfc/rfc1073.txt
        :param tsocket: telnet socket object
        :param command: telnet Command
        :param option: telnet option
        :return: None
        """
        if command == DO and option == NAWS:
            width_short = struct.pack('!H', width)
            height_short = struct.pack('!H', 80)
            tsocket.send(IAC + WILL + NAWS)
            tsocket.send(IAC + SB + NAWS +
                         width_short + height_short +
                         IAC + SE)
        # -- below code taken from telnetlib source
        elif command in (DO, DONT):
            tsocket.send(IAC + WONT + option)
        elif command in (WILL, WONT):
            tsocket.send(IAC + DONT + option)

    return set_max_window_size


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

    def start(self, width=1024):
        self._shell = telnetlib.Telnet(self.host, self.port,
                                       self.timeout)
        self._shell.set_option_negotiation_callback(build_callback(width))

        return self

    def stop(self):
        self._shell.close()

    def send(self, data):
        self._shell.write(data)

    def recv(self, bytes_to_recv):
        # bytes_to_recv is ignored since telnetlib doesn't need it
        return self._shell.read_some()
