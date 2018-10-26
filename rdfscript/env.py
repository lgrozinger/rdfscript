import rdflib

import rdfscript.objects

class Env:
    def __init__(self, repl=False):
        self.g = rdflib.Graph()
        self.symbol_table  = {}
        self.interactive_mode = repl

    ## unnecessary?
    def add_triple(self, s, p, o):
        self.g.add( (s, p, o) )

    def symbol_bind(self, name, value):
        self.symbol_table[name] = value
        return self.symbol_lookup(name)

    def symbol_lookup(self, name):
        value = self.symbol_table.get(name, None)
        if not value:
            return name
        else:
            return value

    def interpret(self, forms):
        result = None

        for form in forms:
            result = form.evaluate(self)

        return result

    def rt_error(self, form):
        # TODO: better, cleaner error handling and reporting
        if self.interactive_mode or not form.lineno:
            print("ERROR: unexpected object %s"
                  % form)
        else:
            print("ERROR: unexpected object %s : LINENO: %d"
                  % (form, form.lineno))
        raise SyntaxError
