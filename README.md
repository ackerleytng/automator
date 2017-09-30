# Automator: An intuitive shell automation tool

Automator is a shell automation tool that gives you intuitive control, as if you are working at an interactive shell.

Automator allows you to send commands to the shell at a prompt, and then receive the response from that command.

Automator works with the ssh and telnet, as well as the local shell.

# Usage

+ [Basic Usage](#basic-usage)
+ [Using `Responses`](#using-responses)
+ [Live results from the automation target!](#live-results-from-the-automation-target)
+ [Interrupt a busy process!](#interrupt-a-busy-process)

## Basic Usage

(Because `echo` works the same way on both Windows and Linux!)

Contents of `examples/hello-world.py`:

```
s = SshShell("192.168.31.140", username="user", password="password").start()
ctrlr = Controller(s).start()

ctrlr.send("echo 'Hello World!'")
response = ctrlr.recv()
sys.stdout.write(ctrlr.motd + ctrlr.prompt + ctrlr.sent_data + response)
```

Output:

```
$ python hello-world.py
Welcome to Ubuntu 16.04.3 LTS (GNU/Linux 4.4.0-96-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  Get cloud support with Ubuntu Advantage Cloud Guest:
    http://www.ubuntu.com/business/services/cloud

25 packages can be updated.
0 updates are security updates.


Last login: Wed Sep 27 12:07:46 2017 from 192.168.31.1
user@telnetd:~$ echo 'Hello World!'
Hello World!
$
```

Same code with a Windows' machine's ip address instead:

```
$ python hello-world.py
Microsoft Windows [Version 6.1.7600]
Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

C:\Users\Administrator\Desktop>echo 'Hello World!'
'Hello World!'

$
```

> I installed freeSSHd on the Windows machine, and
>
> + Unchecked "Use new console engine" on the SSH tab in freeSSHd settings
> + Set up a user named `user`, with "Password stored as SHA1 hash"

## Using `Responses`

Responses are used to guide automator. Here's telnet, done manually:

(I passed `USER=` to prevent my username from being used remotely)

```
$ USER= telnet 192.168.31.131
Trying 192.168.31.131...
Connected to 192.168.31.131.
Escape character is '^]'.
telnetd login: user
Password:
Last login: Wed Sep 27 12:36:41 UTC 2017 from 192.168.31.1 on pts/0
Welcome to Ubuntu 16.04.3 LTS (GNU/Linux 4.4.0-96-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  Get cloud support with Ubuntu Advantage Cloud Guest:
    http://www.ubuntu.com/business/services/cloud

25 packages can be updated.
0 updates are security updates.


user@telnetd:~$ exit
logout
Connection closed by foreign host.
$
```

`telnet` pauses at `login: `, waiting for input, and again at `Password: `. 

To allow `Controller.recv()` to handle these prompts, we can capture `Responses` like this and have it passed to the `Controller`'s `start()` function:

```
s = TelnetShell("192.168.31.131", username="user", password="password").start()

r = Responses([
    ("login:", "user"),
    ("Password:", "password")
])
ctrlr = Controller(s).start(responses=r)
```

> See more in `examples/uptime.py`

### Mechanics of `Responses`

+ Automator will send the response paired with the first prompt in the array that matches
+ A 'match' occurs if the prompt was anywhere in received data before input is expected
+ If there is more than one prompt that matches, the response that had been sent the least often will be sent again
+ Identical prompts may be used to get automator to send certain replies in order
    + For example, the following will also be able to guide automator to complete a connection to the same Telnet server used above:
    ```
    r = Responses([
        (":", "user"),
        (":", "password"),
    ])
    ```
+ If there is no prompt, the following could also be used for the same effect (could result in the responses being sent too many times)
    ```
    r = Responses([
        ("", "user"),
        ("", "password"),
    ])
    ```

## Live results from the automation target!

With `Controller.recv_live()`, you can receive data coming in from the automation target as it happens!

For all those times that you're automating something that takes a while, and you kind of want to watch the responses but don't want to type command by command, manually:

```
import sys

from automator.ssh_shell import SshShell
from automator.controller import Controller

s = SshShell("192.168.31.131", username="user", password="password").start()
ctrlr = Controller(s).start()

ctrlr.send("ping -c 4 localhost")
for l in ctrlr.recv_live():
    sys.stdout.write(l)
```

![ping](ping.gif)

## Interrupt a busy process!

Feel like pressing Ctrl-C, but programmatically? (`examples/ping-ctrl-c.py`)

```
ctrlr.send("ping localhost")
for i, l in enumerate(ctrlr.recv_live()):
    sys.stdout.write(l)

    if i == 4:
        # "\x03" is Ctrl-C
        ctrlr.send_bytes("\x03")
```

![ping-ctrl-c](ping-ctrl-c.gif)

> `Controller.send_bytes()` sends raw bytes, without appending "\n" like `Controller.send()` does.

# Installation

> I'll put this on pypi soon, meanwhile...

## Installation for developers

```
git clone https://github.com/ackerleytng/automator.git
cd automator
pip install -e .
```

