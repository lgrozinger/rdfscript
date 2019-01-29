import rdflib

from .core import Uri, Value
from .error import InternalError, PrefixError
from pysbolgraph.SBOL2Serialize import serialize_sboll2
from pysbolgraph.SBOL2Graph import SBOL2Graph


class RDFData(object):

    def __init__(self, serializer=None):

        self._g = rdflib.Graph()
        self._serializer = serializer

    @property
    def lang_ns(self):
        return rdflib.Namespace('http://github.com/lgrozinger/rdfscript/lang/')

    @property
    def namespace(self):
        return self.from_rdf(self._g.identifier)

    def add(self, s, p, o, unique=False):
        triple = (self.to_rdf(s), self.to_rdf(p), self.to_rdf(o))
        if unique:
            self._g.set(triple)
        else:
            self._g.add(triple)

    def get(self, s, p, o):
        triple = (s, p, o)
        triple = tuple(self.to_rdf(t) if t is not None else t for t in triple)

        results = self._g.triples(triple)
        return [tuple(self.from_rdf(t) for t in triple) for triple in results]

    def remove(self, s, p, o):
        triple = (self.to_rdf(s), self.to_rdf(p), self.to_rdf(o))

        self._g.remove(triple)

    def remove_all(self):
        self._g.remove((None, None, None))
        assert len(self.triples) == 0

    @property
    def triples(self):
        triples = self._g.triples((None, None, None))

        return [tuple(self.from_rdf(t) for t in triple) for triple in triples]

    def bind_prefix(self, prefix, uri):
        u = self.to_rdf(uri)
        self._g.bind(prefix, u)
        return prefix

    def uri_for_prefix(self, prefix):

        namespaces = self._g.namespaces()
        matching = [n for (p, n) in namespaces if p == prefix]

        if len(matching) == 1:
            return self.from_rdf(rdflib.Namespace(matching[0]))
        elif len(matching) == 0:
            raise PrefixError(None, None)
        else:
            raise InternalError(prefix)

    def prefix_for_uri(self, uri):

        u = self.to_rdf(uri)
        namespaces = self._g.namespaces()
        matching = [p for (p, n) in namespaces if n == u]

        if len(matching) == 1:
            return matching[0]
        elif len(matching) == 0:
            raise PrefixError(uri, uri.location)

    def serialise(self):
        if self._serializer == 'rdfxml':
            return self._g.serialize(format='xml').decode("utf-8")
        elif self._serializer == 'nt':
            return self._g.serialize(format='nt').decode("utf-8")
        elif self._serializer == 'n3':
            return self._g.serialize(format='n3').decode("utf-8")
        elif self._serializer == 'turtle':
            return self._g.serialize(format='turtle').decode("utf-8")
        elif self._serializer == 'sbolxml':
            pysbolG = SBOL2Graph()
            pysbolG.g = self._g
            return serialize_sboll2(pysbolG).decode("utf-8")
