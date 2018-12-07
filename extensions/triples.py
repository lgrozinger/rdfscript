import rdflib

class TriplePack(object):
    """
    The object passed to an extensions' run() method.

    triples : a list of 3-tuples whose members are Uri or Value
              language objects.

    bindings : a dictionary with Uri language objects as keys, and
               language objects as values.

    templates : a dictionary with Uri language objects as keys, and
                Template objects as values.
    """

    def __init__(self, triples, bindings, templates):

        self._triples = triples
        self._bindings = bindings
        self._templates = templates

    @property
    def triples(self):
        return self._triples

    @property
    def bindings(self):
        return self._bindings

    @property
    def templates(self):
        return self._templates

    @property
    def subjects(self):
        return set([s for (s, p, o) in self.triples])

    @property
    def predicates(self):
        return set([p for (s, p, o) in self.triples])

    @property
    def objects(self):
        return set([o for (s, p, o) in self.triples])

    def search(self, pattern):
        (s, p, o) = pattern

        def matcher(triple):
            (x, y, z) = triple
            return ((x == s or not s) and
                    (y == p or not p) and
                    (z == o or not o))

        return [t for t in self.triples if matcher(t)]

    def has(self, owner, what):
        results = self.search((owner, what, None))
        return len(results) > 0

    def has_unique(self, owner, what):
        results = self.search((owner, what, None))
        return len(results) == 1

    def value(self, owner, what):
        values = [o for (s, p, o) in self.search((owner, what, None))]
        if len(values) == 0:
            return None
        elif len(values) == 1:
            return values[0]
        else:
            return values

    def add(self, triple):
        # check types are Uri and Value TODO
        self.triples.append(triple)
        return triple

    def set(self, owner, what, value):
        # check types are Uri and Value TODO
        if self.has(owner, what):
            triples = self.search((owner, what, None))
            for triple in triples:
                self.triples.remove(triple)
            self.add((owner, what, value))
            return (owner, what, value)
        else:
            return None

    def lookup(self, uri):
        return self._bindings.get(uri, None)

    def lookup_template(self, uri):
        return self._templates.get(uri, None)
