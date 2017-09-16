class Responses(object):
    def __init__(self, pairs):
        if not isinstance(pairs, list):
            pairs = list(pairs)

        assert all([isinstance(p, tuple) and len(p) == 2 for p in pairs])

        self._pairs = pairs

    def find_first_response(self, string):
        for k, v in self._pairs:
            if k in string:
                return v

        return None

    def update_response(self, string, response):
        r = self.find_first_response(string)
        if r:
            return r
        else:
            return response

    def use(self, response):
        self._pairs = [(k, v) for k, v in self._pairs if v == response]
