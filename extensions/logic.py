import pdb

class And:

    def __init__(self, sub_exts):
        self._sub_exts = [ext for ext in sub_exts]
        self._failure_message = ""

    def run(self, triples, env):
        new_triples = [t for t in triples]
        for ext in self._sub_exts:
            new_triples = ext.run(new_triples, env)
            if not new_triples:
                self._failure_message = ext.failure_message
                return None

        return new_triples

    @property
    def failure_message(self):
        return self._failure_message

class Or:

    def __init__(self, sub_exts):
        self._sub_exts = sub_exts
        self._failure_message = ""

    def run(self, triples, env):
        for ext in self._sub_exts:
            new_triples = ext.run(triples, env)
            if new_triples:
                return new_triples
            else:
                pass

        self._failure_message = sub_exts[0].failure_message
        return None

    @property
    def failure_message(self):
        return self._failure_message
