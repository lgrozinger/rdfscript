import rdfscript.graph as graph
import rdfscript.error as error
import rdfscript.core as core
import rdfscript.resource_handler as handlers
import rdfscript.utils as utils


class Runtime:

    def __init__(self):

        self._g = graph.EnvironmentGraph()
        self._root = self._g.root
        self._resolver = handlers.Resolver(self._g)
        self._creator = handlers.Creator(self._g)

    @property
    def prefix(self):
        prefix = None
        try:
            prefix = self._g.uri_to_prefix(self._root)
        except error.PrefixError:
            pass

        return prefix

    @prefix.setter
    def prefix(self, new_prefix):
        uri = self._g.prefix_to_uri(new_prefix)
        self._root = uri

    def add_prefix(self, name, uri):
        self._g.bind_prefix(name, uri)

    def bind(self, what, where):
        self._creator.create(where, what)

    def binding(self, where):
        return self._resolver.resolve(where)

    def bound_p(self, where):
        result = False
        context = self._g.root_context
        if isinstance(where.names[0], core.Uri):
            context = self._g.get_context(where.names[0])
            where = core.Name(*where.names[1:], location=where.location)
        try:
            result = self._resolver.resolve(where, context=context) is not None
        except error.UnexpectedType:
            pass

        return result
