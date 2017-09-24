import subprocess
import os
import pty


from shell import Shell


class LocalShell(Shell):
    def __init__(self):
        super(LocalShell, self).__init__()

        self._fileno = None
        self._process = None

    def fileno(self):
        if self._fileno is None:
            self.start()

        return self._fileno

    def start(self):
        master, slave = pty.openpty()

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
        }

        self._process = subprocess.Popen(["bash", "-i"],
                                         env=clean_env,
                                         preexec_fn=os.setsid,
                                         close_fds=True,
                                         stdin=slave, stdout=slave,
                                         stderr=slave)
        self._fileno = master

        return self

    def stop(self):
        self.send("exit\n")

        os.close(self._fileno)
        self._fileno = None

        output = self._process.wait()
        if output != -1:
            # Popen.wait() returns -N on unix where N indicates that the child
            #   was terminated by signal N.
            # Signal 1 is SIGHUP (Hangup detected on controlling terminal),
            #   which is ok I think.
            raise OSError("bash -i did not exit properly. {}".format(output))

        self._process = None

    def send(self, data):
        os.write(self._fileno, data)

    def recv(self, bytes_to_recv):
        return os.read(self._fileno, bytes_to_recv)
