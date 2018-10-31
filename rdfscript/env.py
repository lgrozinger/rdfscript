import rdflib

import rdfscript.toplevel
from rdfscript.identifier import URI

class Env:
    def __init__(self, repl=False):
        self.g = rdflib.Graph()
        self.interactive_mode = repl

        ## TODO: make these env-specific and 'hard-to-clash'
        self.default_namespace = rdflib.Namespace('file://rdfscript.env.sbol/')
        self.env_namespace     = rdflib.Namespace('file://rdfscript.env.sbol/')
        self.assign_predicate  = self.env_namespace['expandsTo']

        self.g.bind('rdfscript', self.env_namespace)

    def get_default_namespace(self):
        return self.default_namespace

    def get_env_namespace(self):
        return self.env_namespace

    def get_assignment_uri(self):
        return self.assign_predicate

    def bind_prefix(self, prefix, uri):
        self.g.bind(prefix, uri)

    def get_ns_for_prefix(self, prefix):
        namespaces = self.g.namespaces()

        matching = [n for (p, n) in namespaces if p == prefix]

        if len(matching) == 1:
            return rdflib.Namespace(matching[0])
        else:
            return None

    def add_triple(self, s, p, o):
        self.g.add( (s, p, o) )

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

class RuntimeGraph:

    def __init__(self):
        pass
