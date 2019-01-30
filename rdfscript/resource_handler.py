import rdfscript.utils as utils
import rdfscript.core as core


class Resolver:

    def __init__(self, env_graph):
        self._graph = env_graph

    def resolve(self, name, context=None):
        if context is None:
            context = self._graph.root_context

        value = None
        steps = name.names
        step = utils.name_to_uri(core.Name(steps[0]))
        if len(steps) == 1:
            value = context.get(step)
        elif len(steps) > 1:
            next_context_uri = context.get(step)
            if next_context_uri:
                utils.type_assert(next_context_uri, core.Uri)
                next_context = self._graph.get_context(next_context_uri)
                next_name = core.Name(*steps[1:])
                value = self.resolve(next_name, context=next_context)
            else:
                value = None

        return value


class Creator:

    def __init__(self, env_graph):
        self._graph = env_graph
        self.resolver = Resolver(env_graph)

    def create(self, name, value, context=None):
        if context is None:
            context = self._graph.root_context

        steps = name.names
        step = utils.name_to_uri(core.Name(steps[0]))
        if len(steps) == 1:
            context.put(value, step)
        elif len(steps) > 1:
            new_context_uri = utils.contextualise_uri(step, context)
            context.put(new_context_uri, step)
            next_context = self._graph.get_context(new_context_uri)
            next_name = core.Name(*steps[1:])
            self.create(next_name, value, context=next_context)
