import unittest
import rdflib

from extensions.triples import TriplePack
from extensions.cardinality import (AtLeastOne,
                                    ExactlyOne,
                                    ExactlyN,
                                    CardinalityError)
from rdfscript.core import (Uri,
                            Value,
                            Name)

from rdfscript.template import (Template,
                                Property,
                                Expansion)
from rdfscript.env import Env

class CardinalityExtensionsTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()

        self.v_uri = Uri('http://test.triplepack/#variable', None)
        self.env.assign(self.v_uri,
                        Value(42, None))

        self.template = Template(Name('A'),
                                  [Name('x'),
                                   Name('y')],
                                  [Property(Name('x'),
                                            Value(42)),
                                   Property(Uri('http://example.eg/predicate'),
                                            Name('y'))],
                                  None,
                                  [])

        self.expansion = Expansion(Name('e'),
                                   Name('A'),
                                   [Value(1),
                                    Value(2)],
                                   [])

        self.env.assign_template(self.template.name.evaluate(self.env),
                                 self.template.as_triples(self.env))
        
        triples = self.expansion.as_triples(self.env)
        bindings = self.env._symbol_table
        templates = self.env._template_table

        self.pack = TriplePack(triples, bindings, templates)

    def test_at_least_one(self):

        triples = list(self.pack.triples)

        with self.assertRaises(CardinalityError):
            ext = AtLeastOne(Uri('http://test.eg/#notthere'))
            ext.run(self.pack)

        ext = AtLeastOne(Uri('http://example.eg/predicate'))
        ext.run(self.pack)

        self.assertEqual(triples, self.pack.triples)

    def test_exactly_one_fails(self):

        with self.assertRaises(CardinalityError):
            ext = ExactlyOne(Uri('http://test.eg/#notthere'))
            ext.run(self.pack)

        with self.assertRaises(CardinalityError):
            ext = ExactlyOne(Uri('http://example.eg/predicate'))
            add = self.pack.search((None, Uri('http://example.eg/predicate'), None))[0]
            self.pack.add(add)
            ext.run(self.pack)

    def test_exactly_one_succeeds(self):

        triples = list(self.pack.triples)
        
        ext = ExactlyOne(Uri('http://example.eg/predicate'))
        ext.run(self.pack)

        self.assertEqual(triples, self.pack.triples)

    def test_exactly_N_fails(self):

        with self.assertRaises(CardinalityError):
            ext = ExactlyN(Uri('http://example.eg/predicate'), 2)
            ext.run(self.pack)

        with self.assertRaises(CardinalityError):
            ext = ExactlyN(Uri('http://example.eg/predicate'), 2)
            add = self.pack.search((None, Uri('http://example.eg/predicate'), None))[0]
            self.pack.add(add)
            self.pack.add(add)
            ext.run(self.pack)

    def test_exactly_N_succeeds(self):

        with self.assertRaises(CardinalityError):
            ext = ExactlyN(Uri('http://example.eg/predicate'), 2)
            ext.run(self.pack)

        ext = ExactlyN(Uri('http://example.eg/predicate'), 2)
        add = self.pack.search((None, Uri('http://example.eg/predicate'), None))[0]
        self.pack.add(add)
        ext.run(self.pack)

