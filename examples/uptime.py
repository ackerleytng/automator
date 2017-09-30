from automator.telnet_shell import TelnetShell
from automator.controller import Controller
from automator.responses import Responses

s = TelnetShell("192.168.31.131", username="user", password="password").start()

r = Responses([
    ("login:", "user"),
    ("Password:", "password"),
])
ctrlr = Controller(s).start(responses=r)

ctrlr.send("uptime")
response = ctrlr.recv()

print repr(ctrlr.motd)
print repr(ctrlr.prompt)
print repr(ctrlr.sent_data)
print repr(response)
