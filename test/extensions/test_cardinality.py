import unittest
import rdflib

from extensions.triples import TriplePack
from extensions.cardinality import (AtLeastOne,
                                    CardinalityError)
from rdfscript.core import (Uri,
                            Value)

from rdfscript.template import (Template,
                                Property,
                                Expansion)
from rdfscript.env import Env

import test.test_helper as test

class CardinalityExtensionsTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()

        self.v_uri = Uri('http://test.triplepack/#variable', None)
        self.env.assign(self.v_uri,
                        Value(42, None))

        self.template = Template(test.name('A'),
                                  [test.name('x'),
                                   test.name('y')],
                                  [Property(test.name('x'),
                                            Value(42, None),
                                            None),
                                   Property(Uri('http://example.eg/predicate', None),
                                            test.name('y'),
                                            None)],
                                  None,
                                  None)

        self.expansion = Expansion(test.name('e'),
                                   test.name('A'),
                                   [Value(1, None),
                                    Value(2, None)],
                                   [],
                                   None)

        self.template.parameterise()
        self.template.de_name(self.env)
        self.env.assign_template(self.template.name, self.template)

        self.expansion.de_name(self.env)
        triples = self.expansion.as_triples(self.env)
        bindings = self.env._symbol_table
        templates = self.env._template_table

        self.pack = TriplePack(triples, bindings, templates)

    def test_at_least_one(self):

        triples = list(self.pack.triples)

        with self.assertRaises(CardinalityError):
            ext = AtLeastOne(Uri('http://test.eg/#notthere', None))
            ext.run(self.pack)

        ext = AtLeastOne(Uri('http://example.eg/predicate', None))
        ext.run(self.pack)

        self.assertEqual(triples, self.pack.triples)
