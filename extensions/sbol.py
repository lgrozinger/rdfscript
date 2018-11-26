import rdflib
import re

class SbolIdentity:

    def __init__(self):
        self._g = rdflib.Graph()
        self._sbolns = rdflib.Namespace(rdflib.URIRef('http://sbols.org/v2#'))
        self._persistent_uri = self._sbolns['persistentIdentity']
        self._display_uri = self._sbolns['displayId']

    def run(self, triples, env):

        for triple in triples:
            self._g.add(triple)

        subjects = self._g.subjects()

        for subject in subjects:
            dId = self.get_display_id(subject)
            if not self.check_persistent_identity(subject, dId):
                self._g.set((subject, self._persistent_uri, rdflib.URIRef(dId, base=subject)))

        return list(self._g.triples((None, None, None)))

    @property
    def failure_message(self):
        return (f"EXTENSION FAILED:\n"
                f"The author does not expect the extension to fail.\n\n")

    def get_display_id(self, subject):

        result = [did for (s, p, did) in self._g.triples((subject, self._display_uri, None))]
        if len(result) > 1:
            self._g.set((subject, self._display_uri, result[0]))
            return result[0].toPython()
        elif len(result) == 1:
            return result[0].toPython()
        else:
            dId = re.split('#|/|:', subject.toPython())[-1]
            self._g.set((subject, self._display_uri, rdflib.Literal(dId)))
            return dId

    def check_persistent_identity(self, subject, displayId):

        result = [pid for (s, p, pid) in self._g.triples((subject, self._persistent_uri, None))]
        if len(result) > 1:
            return False
        elif len(result) == 1:
            dId = re.split('#|/|:', result[0].toPython())[-1]
            return dId == displayId
