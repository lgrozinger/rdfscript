import rdflib

import rdfscript.toplevel
from rdfscript.identifier import QName, NSPrefix, LocalName

class Env:
    def __init__(self, repl=False):
        self.g = rdflib.Graph()
        self.symbol_table  = {}
        self.interactive_mode = repl

        ## TODO: make these env-specific and 'hard-to-clash'
        self.default_namespace = 'http://rdfscript/debug#'
        self.env_namespace     = self.default_namespace
        self.assign_predicate  = 'evaluatesTo'

    def get_default_namespace(self):
        return NSPrefix(LocalName(self.default_namespace, 0), 0)

    def get_env_namespace(self):
        return NSPrefix(LocalName(self.env_namespace, 0), 0)

    def get_assignment_qname(self):
        return QName(self.get_env_namespace(),
                     LocalName(self.assign_predicate, 0),
                     0)

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
