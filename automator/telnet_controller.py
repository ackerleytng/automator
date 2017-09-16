from controller import Controller


class TelnetController(Controller):
    def __init__(self, name, shell):
        super(TelnetController, self).__init__(shell)
        self.name = name
