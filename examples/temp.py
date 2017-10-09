import sys

from pynomator.ssh_shell import SshShell
from pynomator.local_shell import LocalShell
from pynomator.telnet_shell import TelnetShell
from pynomator.controller import Controller
from pynomator.responses import Responses

s = TelnetShell("192.168.31.131", username="user", password="password").start()
# s = LocalShell().start()
r = Responses([
    ("login:", "user"),
    ("Password:", "password")
])
ctrlr = Controller(s).start(responses=r)

ctrlr.send("echo 'Hello World!'")
response = ctrlr.recv()
sys.stdout.write(ctrlr.motd + ctrlr.prompt + ctrlr.sent_data + response)
"""

ctrlr.send("dir")
response = ctrlr.recv()
print ctrlr.motd + ctrlr.prompt + ctrlr.sent_data + response
"""
