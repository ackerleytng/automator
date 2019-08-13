class Responses(object):
    def __init__(self, pairs=[]):
        if not isinstance(pairs, list):
            pairs = list(pairs)

        assert all([isinstance(p, tuple) and len(p) == 2 for p in pairs])

        # self._pairs is a list of tuples, where each tuple is
        #   (prompt, response, usage count)
        self._pairs = [(k, v, 0) for k, v in pairs]

    def find_response(self, string):
        """Pick the first valid (prompt is in string) response
        that has the lowest usage count
        """

        valid_responses = [(k, v, count) for k, v, count in self._pairs
                           if k in string]

        if not valid_responses:
            return None

        return min(valid_responses, key=lambda p: p[2])

    def update_response(self, string, response):
        instance = self.find_response(string)
        if instance:
            return (instance[1], instance)
        else:
            return (None, response)

    def use(self, instance):
        self._pairs = [(k, v, count + 1 if (k == instance[0] and
                                            v == instance[1]) else count)
                       for k, v, count in self._pairs]
