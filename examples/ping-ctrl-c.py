import sys

from pynomator.ssh_shell import SshShell
from pynomator.controller import Controller

s = SshShell("192.168.31.131", username="user", password="password").start()
ctrlr = Controller(s).start()

ctrlr.send("ping localhost")
for i, l in enumerate(ctrlr.recv_live()):
    sys.stdout.write(l)

    if i == 4:
        # "\x03" is Ctrl-C
        ctrlr.send_bytes("\x03")
