import re
import pdb

from .logic import And
from .error import ExtensionError

class SBOL2:

    def __init__(self):

        self._sbolns = Uri('http://sbols.org/v2#', None)
        self._toplevels = [Uri(self._sbolns.uri + tl, None) for tl
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
    def persistentIdUri(self):
        return Uri(self.namespace.uri + 'persistentIdentity', None)

    @property
    def displayIdUri(self):
        return Uri(self.namespace.uri + 'displayId', None)

    @property
    def versionUri(self):
        return Uri(self.namespace.uri + 'version', None)

    def is_toplevel(self, possible_toplevel):
        return (isinstance(possible_toplevel, Uri) and
                possible_toplevel in self._toplevels)

class SbolIdentity:

    def __init__(self):
        pass

    def run(self, triplepack):

        subjects = triplepack.subjects
        return And([SBOLCompliant(s) for s in subjects]).run(triplepack)

class SBOLCompliant:

    def __init__(self, for_subject):
        self._sbol = SBOL2()
        self._subject = for_subject

    @property
    def sbol(self):
        return self._sbol

    class SBOLComplianceError(ExtensionError):

        def __init__(self, helpful_message):
            self._type = 'SBOL2 Compliant URI error'
            self._helpful_message = helpful_message

        def __str__(self):
            return ExtensionError.__str__(self) + format(" %s\n" % self._helpful_message)

    def run(self, triplepack):

        if triplepack.has(self._subject, self.sbol.persistentIdUri):
            persistentId = triplepack.value((self._subject, self.sbol.persistentIdUri, None))
        else:
            triplepack.set((self._subject,
                            self.sbol.persistentIdUri,
                            self.compute_persistentId(self._subject)))

        displayId = triplepack.value((self._subject, self.sbol.persistentIdUri, None))

        if not triplepack.has_unique(self._subject, self.sbol.persistentIdUri):
            message = format("The SBOL2 object %s has been given more than 1 persistentIdentity."
                             % self._subject)
            raise SBOLComplianceError(message)

        if not triplepack.has_unique(self._subject, self.sbol.displayIdUri):
            message = format("The SBOL2 object %s has been given more than 1 displayId."
                             % self._subject)
            raise SBOLComplianceError(message)

        dId = re.split('#|/|:', persistentId.value)[-1]
        if dId == displayId.value:
                return triples
            else:
                triples.remove(persistentId[0])
                return self.run(triples, env)

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
            sbol_type = [o for (s, p, o) in triples if p == rdflib.RDF.type and s == self._subject]
            if len(sbol_type) == 1:
                return triples + [(self._subject, self.sbol.persistentIdUri, self.compute_persistentId(triples))]
            else:
                self._failure_message = "SBOL objects must have exactly one type"
                return None

    def compute_persistentId(self, triplepack, subject):
        ## TODO: check for top level, compute persistentId accordingly
        if not triplepack.has_unique(subject, Uri(rdflib.RDF.type, None)):
            raise self.
        sbol_type = triplepack.value(subject, Uri(rdflib.RDF.type, None))
        sbol_type = [o for (s, p, o) in triples if p == rdflib.RDF.type and s == self._subject][0]

        if self.sbol.is_toplevel(sbol_type):
            return self._subject
        else:
            parent = [s for (s, p, o) in triples if o == self._subject][0]
            dId    = [o for (s, p, o) in triples if p == self.sbol.displayIdUri][0]
            return rdflib.Namespace(parent)['#' + dId.toPython()]

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
                     if (p == self.sbol.displayIdUri and
                         s == self._subject)]

        if len(displayId) > 1:
            triples.remove(displayId[0])
            return self.run(triples, env)
        elif len(displayId) == 1:
            return triples
        else:
            triples.append((self._subject, self.sbol.displayIdUri, self.compute_displayId()))
            return triples

    def compute_displayId(self):

        dId = re.split('#|/|:', self._subject.toPython())[-1]
        return rdflib.Literal(dId)
