import rdflib

import rdfscript.utils as utils


class Context:

    def __init__(self, context_graph):

        self._graph = context_graph
        self._root = self._graph.identifier

    @property
    def root(self):
        return utils.from_rdf(self._root)

    def put(self, what, where):
        triple = (self.root, where, what)
        self._graph.set(utils.to_rdf_triple(triple))
        return triple

    def get(self, what):
        search = (self._root, utils.to_rdf(what), None)
        result = self._graph.triples(search)
        result = [utils.from_rdf(o) for (s, p, o) in result]
        assert len(result) <= 1
        try:
            result = result[0]
        except IndexError:
            result = None

        return result

    def get_all(self):
        return [t[2] for t in self.get_all_triples()]

    def get_all_triples(self):
        raw_triples = self._graph.triples((None, None, None))
        return utils.from_rdf_triples(raw_triples)
