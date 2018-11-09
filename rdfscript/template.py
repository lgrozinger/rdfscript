import rdflib

from rdfscript.toplevel import ScriptObject, Assignment, InstanceExp
from rdfscript.identifier import LocalName

class ConstructorApp(ScriptObject):

    def __init__(self, identifier, args, linenum):
        super().__init__(linenum)

        self.identifier = identifier
        self.args       = args

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.identifier == other.identifier and
                self.args == other.args)

    def __repr__(self):
        return format("CONSTRUCTORAPP: (%s, with args: %s)" %
                      (self.identifier, self.args))


def get_template_graph(graph,

def get_subgraph(graph, identifier):

        subgraph = rdflib.Graph()

        ## all with subject 'identifier'
        for p, o in self.g[identifier]:
            subgraph.add((identifier, p, o))
            if isinstance(o, rdflib.URIRef):
                subgraph += self.get_subgraph(o)

        return subgraph

