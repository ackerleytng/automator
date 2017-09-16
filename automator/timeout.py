class Timeout(Exception):
    def __init__(self, msg):
        super(Timeout, self).__init__(msg)
