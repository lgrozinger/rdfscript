import rdfscript.utils as utils


class Context:

    def __init__(self, context_graph):
        self._graph = context_graph
        self._root = self._graph.identifier

    def __eq__(self, other):
        return isinstance(other, Context) \
            and self.triples == other.triples

    @property
    def root(self):
        return utils.from_rdf(self._root)

    @property
    def triples(self):
        raw_triples = self._graph.triples((None, None, None))
        return utils.from_rdf_triples(raw_triples)

    def put(self, what, where):
        rdf_where = utils.to_rdf(where)
        rdf_what = utils.to_rdf(what)
        triple = (self._root, rdf_where, rdf_what)
        self._graph.set(triple)
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

    def out_edges(self):
        search = (self._root, None, None)
        result = self._graph.triples(search)
        result = utils.from_rdf_triples(result)
        return [(t[1], t[2]) for t in result]

    def get_all(self):
        return [(t[1], t[2]) for t in self.triples]
