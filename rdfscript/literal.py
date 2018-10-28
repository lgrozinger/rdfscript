import rdflib

from rdfscript.toplevel import ScriptObject

class Literal(ScriptObject):

    def __init__(self, lexical_value, line_num):
        super().__init__(line_num)
        self.value = rdflib.Literal(lexical_value)

        self.datatype = self.value.datatype

    def __eq__(self, other):
        return self.value == other.value

    def evaluate(self, env):
        return self.value
