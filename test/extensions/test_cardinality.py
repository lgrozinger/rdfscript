import unittest
import rdflib

from extensions.triples import TriplePack
from extensions.cardinality import (AtLeastOne,
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
