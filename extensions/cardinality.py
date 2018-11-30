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
        return ("EXTENSION FAILED:\n" + 
                format("Reason: At least one value for property %s" % self._prop) +
                " was expected.\nNone were found.")
