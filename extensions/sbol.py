import rdflib
import re
import pdb

from .logic import And

class SBOL2:

    def __init__(self):

        self._sbolns = rdflib.Namespace(rdflib.URIRef('http://sbols.org/v2#'))
        self._toplevels = [self._sbolns[tl] for tl
                           in ['Sequence',
                               'ComponentDefinition',
                               'ModuleDefinition',
                               'Model',
                               'Collection',
                               'GenericTopLevel',
                               'Attachment',
                               'Activity',
                               'Agent',
                               'Plan',
                               'Implementation',
                               'CombinatorialDerivation']]

    @property
    def namespace(self):
        return self._sbolns

    @property
    def persistentIdURI(self):
        return self.namespace['persistentIdentity']

    @property
    def displayIdURI(self):
        return self.namespace['displayId']

    @property
    def versionURI(self):
        return self.namespace['version']

    def is_toplevel(self, possible_toplevel):
        return (isinstance(possible_toplevel, rdflib.URIRef) and
                possible_toplevel in self._toplevels)

class SbolIdentity:

    def __init__(self):
        self._g = rdflib.Graph()

    def run(self, triples, env):

        for triple in triples:
            self._g.add(triple)

        subjects = self._g.subjects()
        return And([And([SBOLDisplayId(s), SBOLPersistentId(s)]) for s in subjects]).run(triples, env)

    @property
    def failure_message(self):
        return (f"EXTENSION FAILED:\n"
                f"The author does not expect the extension to fail.\n\n")

class SBOLPersistentId:

    def __init__(self, for_subject):
        self._sbol = SBOL2()
        self._subject = for_subject

    @property
    def sbol(self):
        return self._sbol

    def run(self, triples, env):

        persistentId = [(s, p, o)
                        for (s, p, o)
                        in triples
                        if (p == self.sbol.persistentIdURI and
                            s == self._subject)]

        displayId = [o for (s, p, o) in triples if p == self.sbol.displayIdURI][0]

        if len(persistentId) > 1:
            triples.remove(persistentId[0])
            return self.run(triples, env)
        elif len(persistentId) == 1:
            (s, p, o) = persistentId[0]
            dId = re.split('#|/|:', o.toPython())[-1]
            if dId == displayId:
                return triples
            else:
                triples.remove(persistentId[0])
                return self.run(triples, env)
        else:
            return triples + [(self._subject, self.sbol.persistentIdURI, self.compute_persistentId())]

    def compute_persistentId(self):
        ## TODO: check for top level, compute persistentId accordingly
        return self._subject

class SBOLDisplayId:

    def __init__(self, for_subject):
        self._sbol = SBOL2()
        self._subject = for_subject

    @property
    def sbol(self):
        return self._sbol

    def run(self, triples, env):

        displayId = [(s, p, o)
                     for (s, p, o)
                     in triples
                     if (p == self.sbol.displayIdURI and
                         s == self._subject)]

        if len(displayId) > 1:
            triples.remove(displayId[0])
            return self.run(triples, env)
        elif len(displayId) == 1:
            return triples
        else:
            triples.append((self._subject, self.sbol.displayIdURI, self.compute_displayId()))
            return triples

    def compute_displayId(self):

        dId = re.split('#|/|:', self._subject.toPython())[-1]
        return rdflib.Literal(dId)
