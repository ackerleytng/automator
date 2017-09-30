import sys

from automator.ssh_shell import SshShell
from automator.controller import Controller

s = SshShell("192.168.31.131", username="user", password="password").start()
ctrlr = Controller(s).start()

ctrlr.send("ping -c 4 localhost")
for l in ctrlr.recv_live():
    sys.stdout.write(l)
