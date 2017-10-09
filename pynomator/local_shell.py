import os
from ptyprocess import PtyProcess

from shell import Shell


class LocalShell(Shell):
    def __init__(self):
        super(LocalShell, self).__init__()

        self._process = None

    def fileno(self):
        if self._process is None:
            self.start()

        return self._process.fileno()

    def start(self, width=1024):
        # 16 to filter out weird environments that people set
        #   (16 will capture /usr/local/sbin)
        clean_path = ':'.join([e for e in os.environ['PATH'].split(':')
                               if len(e) < 16])
        clean_env = {
            "PATH": clean_path,
            "PS1": "\u@\h \\$ ",
            "TERM": "xterm-256color",
            "USER": os.environ["USER"],
            "PWD": os.environ["PWD"],
            "HOME": os.environ["HOME"],
            "LANG": os.environ["LANG"],
            "COLUMNS": "1024",
        }

        self._process = PtyProcess.spawn(["sh"],
                                         env=clean_env,
                                         dimensions=(width, 80))

        return self

    def stop(self):
        self.send("exit\n")

        self._process.close()
        self._process = None

    def send(self, data):
        self._process.write(data)

    def recv(self, bytes_to_recv):
        # Not completely sure if hard-coding this to 1024 is right
        return self._process.read(1024)
