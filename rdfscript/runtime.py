import rdfscript.graph as graph
import rdfscript.error as error
import rdfscript.utils as utils
import rdfscript.core as core
import rdfscript.resource_handler as handlers


class Runtime:

    def __init__(self):

        self._g = graph.Graph()
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
        if self.prefix is not None:
            steps = self.prefix.names + where.names
            where = core.Name(*steps, location=where.location)

        binding = self.binding(where)
        if binding is not None:
            raise error.Binding(where, binding, where.location)

        return self._creator.create(where, what)

    def binding(self, where):
        binding = None
        if self.prefix is not None:
            steps = self.prefix.names + where.names
            prefixed_where = core.Name(*steps, location=where.location)
            binding = self._resolver.resolve(prefixed_where)

        return binding or self._resolver.resolve(where)

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

    def context(self, where):
        context = None

        if isinstance(where, core.Uri):
            context = self._g.get_context(where)
        else:
            uri = self.binding(where)
            if uri is not None:
                utils.type_assert(uri, core.Uri)
                context = self._g.get_context(uri)

        return context

    def graph_dump(self):
        print(self._g.graph.serialize(format='turtle').decode("utf-8"))
