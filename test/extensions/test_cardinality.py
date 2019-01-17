import unittest

from extensions.triples import TriplePack
from extensions.cardinality import (AtLeastOne,
                                    ExactlyOne,
                                    ExactlyN,
                                    CardinalityError)
import rdfscript.core as core

from rdfscript.template import (Template,
                                Property,
                                Expansion)
from rdfscript.env import Env


class CardinalityExtensionsTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()

        self.v_uri = core.Uri('http://test.triplepack/#variable', None)
        do_assign(self.v_uri, core.Value(42), self.env)

        self.template = Template(core.Name('A'),
                                 [core.Name('x'),
                                  core.Name('y')],
                                 [Property(core.Name('x'),
                                           core.Value(42)),
                                  Property(core.Uri('http://example.eg/predicate'),
                                           core.Name('y'))])

        self.expansion = Expansion(core.Name('e'),
                                   core.Name('A'),
                                   [core.Value(1),
                                    core.Value(2)],
                                   [])

        self.template.evaluate(self.env)

        def triple_eval(triple):
            (s, p, o) = triple
            s = s.evaluate(self.env)
            p = p.evaluate(self.env)
            o = o.evaluate(self.env)

            return (s, p, o)

        triples = self.expansion.as_triples(self.env)
        triples = [triple_eval(triple) for triple in triples]

        bindings = self.env._rdf.get(None, core.identity, None)
        symbol_table = dict()
        for (s, p, o) in bindings:
            symbol_table[s] = o

        templates = self.env._template_table

        self.pack = TriplePack(triples, symbol_table, templates)

    def test_at_least_one(self):

        triples = list(self.pack.triples)

        with self.assertRaises(CardinalityError):
            ext = AtLeastOne(core.Uri('http://test.eg/#notthere'))
            ext.run(self.pack)

        ext = AtLeastOne(core.Uri('http://example.eg/predicate'))
        ext.run(self.pack)

        self.assertEqual(triples, self.pack.triples)

    def test_exactly_one_fails(self):

        with self.assertRaises(CardinalityError):
            ext = ExactlyOne(core.Uri('http://test.eg/#notthere'))
            ext.run(self.pack)

        with self.assertRaises(CardinalityError):
            ext = ExactlyOne(core.Uri('http://example.eg/predicate'))
            add = self.pack.search(
                (None, core.Uri('http://example.eg/predicate'), None))[0]
            self.pack.add(add)
            ext.run(self.pack)

    def test_exactly_one_succeeds(self):

        triples = list(self.pack.triples)

        ext = ExactlyOne(core.Uri('http://example.eg/predicate'))
        ext.run(self.pack)

        self.assertEqual(triples, self.pack.triples)

    def test_exactly_N_fails(self):

        with self.assertRaises(CardinalityError):
            ext = ExactlyN(core.Uri('http://example.eg/predicate'), 2)
            ext.run(self.pack)

        with self.assertRaises(CardinalityError):
            ext = ExactlyN(core.Uri('http://example.eg/predicate'), 2)
            add = self.pack.search(
                (None, core.Uri('http://example.eg/predicate'), None))[0]
            self.pack.add(add)
            self.pack.add(add)
            ext.run(self.pack)

    def test_exactly_N_succeeds(self):

        with self.assertRaises(CardinalityError):
            ext = ExactlyN(core.Uri('http://example.eg/predicate'), 2)
            ext.run(self.pack)

        ext = ExactlyN(core.Uri('http://example.eg/predicate'), 2)
        add = self.pack.search(
            (None, core.Uri('http://example.eg/predicate'), None))[0]
        self.pack.add(add)
        ext.run(self.pack)


def do_assign(name, value, env):
    core.Assignment(name, value).evaluate(env)
