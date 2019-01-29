import rdfscript.graph as graph
import rdfscript.resource_handler as handlers

class Runtime:

    def __init__(self):

        self._g = graph.EnvironmentGraph()
        self._resolver = handlers.Resolver(self._g)
        self._creator = handlers.Creator(self._g)

    @property
    def prefix(self):
        return self._g.root
