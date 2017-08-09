Target
+ has one tunnel
+ has many thread-safe pipes 

[
Tunnel
has
+ destination
can
+ construct pipes
+ report breakage (exception)
]

Pipe
[
has
+ tunnel
]
can
+ send
+ receive reply
+ report breakage (exception)

Manager
has
+ associated pipe
+ shell prompt (e.g. "[user@localhost] ~ $", #, bash4.4 #"
can
+ send keystroke
+ send command
+ parse response, return (status, reply), status = [ok, dunno what to do,]
how

send command is a coroutine that will, start event loop with sending queue
in event loop
+ send
+ receive
+ process
  + add receive and send tasks as necessary until all tasks are done
+ forward received lines or partial messages to caller

Tester
can
+ send command
+ forward partial reply
  + print partial reply if necessary
+ check reply with checker

Checker
can
+ check messages
