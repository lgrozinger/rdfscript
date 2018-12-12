import unittest
import logging

import rdflib

from rdfscript.env import Env
from rdfscript.core import (Name,
                            Value,
                            Uri)

class EnvTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()

    def tearDown(self):
        None

    @unittest.skip("prefix binding has changed")
    def test_prefix_binding(self):

        prefix_uri = Uri('http://test.prefix.eg/', None)
        prefix = Prefix('x', None)

        self.env.bind_prefix(prefix, prefix_uri)

        name = Name(prefix, LocalName('local', None), None)
        resolved_uri = self.env.resolve_name(name)
        self.assertEqual(resolved_uri, Uri('http://test.prefix.eg/local', None))

    @unittest.skip("prefix binding has changed")
    def test_get_and_set_default_prefix(self):

        prefix = Prefix('x', None)
        self.env.bind_prefix(prefix, Uri('http://eg/', None))
        before = Uri(self.env._rdf._g.identifier.toPython(), None)
        self.assertEqual(Prefix(before, None), self.env.default_prefix)

        self.env.set_default_prefix(prefix)
        self.assertEqual(prefix, self.env.default_prefix)

    def test_assignment(self):

        uri = Uri('http://test.variable/#x')
        value = Value(12345)

        self.env.assign(uri, value)
        self.assertEqual(self.env._symbol_table.get(uri), value)

    def test_lookup(self):

        # assume test_assignment passed
        uri = Uri('http://test.variable/#x')
        value = Value(12345)

        self.env.assign(uri, value)
        self.assertEqual(self.env.lookup(uri), value)


    @unittest.skip("Not yet refactored template")
    def test_template_binding(self):

        template = Template(Name(None, 'template', None),
                            [Name(None, 'x', None)],
                            [Property(Name(None, 'x', None), Value(42, None), None)],
                            None,
                            None)

        evaluate(template, self.env)

        stored_template = self.env.lookup_template(self.env.resolve_name(None, 'template'))

        self.assertEqual(stored_template, template)
