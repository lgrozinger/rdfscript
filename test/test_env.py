import unittest
import logging

import rdflib

from rdfscript.env import Env
from rdfscript.core import (Name, Value, Uri)
from rdfscript.templating import (Template,
                                  Parameter,
                                  Property)

from rdfscript.evaluate import evaluate

class EnvTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()

    def tearDown(self):
        None

    def test_prefix_binding(self):

        with self.assertRaises(Exception):
            self.env.resolve_name('prefix', 'local')

        prefix_uri = 'http://test.prefix.eg/'

        self.env.bind_prefix('prefix', rdflib.URIRef(prefix_uri))

        resolved_name = self.env.resolve_name('prefix', 'local')
        self.assertEqual(resolved_name, rdflib.URIRef('local', base=prefix_uri))

    def test_template_binding(self):

        template = Template(Name(None, 'template', None),
                            [Parameter('x', 0, None)],
                            [Property(Name(None, 'x', None), Value(42, None), None)],
                            None)

        evaluate(template, self.env)

        template_triples = self.env.get_template(self.env.resolve_name(template.name.prefix,
                                                                       template.name.localname))


        self.assertEqual(len(template_triples), 2)
