import rdflib
import importlib

class ExtensionManager:

    def __init__(self, extras=[]):

        self._extensions = {}
        self.add_extra_extension('extensions.cardinality.AtLeastOne',
                                 shortname='AtLeastOne')
        for name in extras:
            self.add_extra_extension(name)

    @property
    def extensions(self):
        return self._extensions.keys()

    def add_extra_extension(self, name, shortname=None):
        if (name in self._extensions or
            (shortname and shortname in self._extensions)):
            raise DuplicateExtension(name)
        else:
            mod, ext = name.rsplit('.', 1)
            mod = importlib.import_module(mod)
            ext = getattr(mod, ext)
            if shortname:
                self._extensions[shortname] = ext
            else:
                self._extensions[name] = ext

    def remove_extension(self, name):
        try:
            del self._extensions[name]
        except KeyError:
            pass

    def get_extension(self, name):
        return self._extensions[name]

class Extension:

    def __init__(self, name, rules):

        self._name = name
        self._rules = rules

    def add_rule(self, rule):
        self._rule.append(rule)

class AndExtension(Extension):

    def __init__(self, name, rules):
        super().__init__(name, rules)

    def run(self, triples, env):
        for rule in self._rules:
            new_triples = rule.run(triples, env)
            if new_triples:
                triples = new_triples
            else:
                return None

        return triples

class OrExtension(Extension):

    def __init__(self, name, rules):
        super().__init__(name, rules)

    def run(self, triples, env):
        for rule in self._rules:
            new_triples = rule.run(triples, env)
            if new_triples:
                return new_triples
            else:
                pass

        return None

class DuplicateExtension(Exception):

    def __init__(self, name):
        self._name = name

    def __str__(self):
        message = (f"ERROR: Extension named {self._name} already exists.\n"
                   f"Choose another name or remove existing extension.\n\n")
        return message
