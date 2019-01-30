import rdflib

import rdfscript.context as context
import rdfscript.error as error
import rdfscript.utils as utils
import rdfscript.core as core


class EnvironmentGraph:

    def __init__(self):

        self._graph = rdflib.ConjunctiveGraph()

    @property
    def graph(self):
        return self._graph

    @property
    def root(self):
        return utils.from_rdf(self.graph.identifier)

    @property
    def root_context(self):
        return self.get_context(self.root)

    def get_context(self, rooted_at):
        rdflib_root = utils.to_rdf(rooted_at)
        rdflib_graph = self.graph.get_context(rdflib_root)
        return context.Context(rdflib_graph)

    def bind_prefix(self, prefix, uri):
        p = prefix.names[0]
        u = utils.to_rdf(uri)
        self.graph.bind(p, u)
        self.root_context.put(uri, core.Uri(p))
        return prefix

    def prefix_to_uri(self, prefix):
        namespaces = self.graph.namespaces()
        matching = [n for (p, n) in namespaces if p == prefix.names[0]]
        if len(matching) == 1:
            matching = utils.from_rdf(matching[0])
        elif len(matching) == 0:
            raise error.PrefixError(prefix, prefix.location)

        return matching

    def uri_to_prefix(self, uri):
        u = utils.to_rdf(uri)
        namespaces = self.graph.namespaces()
        matching = [p for (p, n) in namespaces if n == u]

        if len(matching) == 1:
            matching = matching[0]
        elif len(matching) == 0:
            raise error.PrefixError(uri, uri.location)

        return core.Name(matching)
