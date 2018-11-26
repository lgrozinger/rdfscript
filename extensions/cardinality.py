import rdflib

class AtLeastOne:

    def __init__(self, property_uri):
        self._prop = property_uri

    def run(self, triples, env):

        results = [p for (s, p, o) in triples if p == self._prop]
        if len(results) > 0:
            return triples
        else:
            return None

    @property
    def failure_message(self):
        return (f"EXTENSION FAILED:\n"
                f"Reason: At least one value for property {self._prop}"
                f" was expected.\nNone were found.")
