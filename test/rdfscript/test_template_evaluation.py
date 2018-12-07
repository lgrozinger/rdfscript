import unittest
import logging

from rdfscript.env import Env
from rdfscript.core import (Value,
                            Uri)
from rdfscript.template import (Template,
                                Property)

from rdfscript.evaluate import evaluate
import test.test_helper as test

class RuntimeIdentifierTest(unittest.TestCase):

    def setUp(self):
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

        self.env = Env()

    def tearDown(self):
        None

    def test_evaluate_template(self):

        self.assertEqual(self.env.lookup_template(self.template.name.uri(self.env)),
                         None)

        evaluate(self.template, self.env)

        self.assertEqual(self.env.lookup_template(self.template.name),
                         self.template)
