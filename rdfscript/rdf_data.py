import rdflib
from .core import Uri, Value
from .error import InternalError, PrefixError
from pysbolgraph.SBOL2Serialize import serialize_sboll2

class RDFData(object):
    """
    This class manages the backend RDF graph.
    It abstracts away rdflib objects and operates only with the core
    language objects Uri and Value.
    """

    def __init__(self, serializer=None):

        self._g = rdflib.Graph()
        self._serializer = serializer

    @property
    def namespace(self):
        return self.from_rdf(self._g.identifier)

    def to_rdf(self, language_object):
        if isinstance(language_object, Uri):
            return rdflib.URIRef(language_object.uri)
        elif isinstance(language_object, Value):
            return rdflib.Literal(language_object.value)
        else:
            raise InternalError(language_object,
                                language_object.location)

    def from_rdf(self, rdf_object):
        if isinstance(rdf_object, rdflib.URIRef):
            return Uri(rdf_object.toPython(), None)
        elif isinstance(rdf_object, rdflib.Literal):
            return Value(rdf_object.toPython(), None)
        elif isinstance(rdf_object, rdflib.Namespace):
            return self.from_rdf(rdflib.URIRef(rdf_object))
        elif isinstance(rdf_object, rdflib.BNode):
            return self.from_rdf(rdflib.URIRef(rdf_object))
        else:
            raise TypeError

    def add(self, s, p, o, unique=False):
        triple = (self.to_rdf(s), self.to_rdf(p), self.to_rdf(o))
        if unique:
            self._g.set(triple)
        else:
            self._g.add(triple)

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
            return serialize_sboll2(self._g).decode("utf-8")
