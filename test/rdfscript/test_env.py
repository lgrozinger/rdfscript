import unittest

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from rdfscript.core import (Name,
                            Value,
                            Uri)


class EnvTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()
        self.parser = RDFScriptParser()

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

    def test_self_uri_init(self):

        self.assertEqual(self.env.current_self, Uri(self.env._rdf._g.identifier.toPython()))

    def test_self_uri_set(self):

        uri = Uri('setselfuri')
        self.env.self_uri = uri
        self.assertEqual(self.env.self_uri, uri)

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

    def test_template_binding(self):

        template = self.parser.parse('t()(x = 1 y = 2)')[0]
        uri = template.name.evaluate(self.env)
        self.assertFalse(self.env.lookup_template(uri))

        self.env.assign_template(uri, template.as_triples(self.env))
        self.assertEqual(self.env._template_table.get(uri, False),
                         template.as_triples(self.env))

    def test_template_lookup(self):

        template = self.parser.parse('t()(x = 1 y = 2)')[0]
        uri = template.name.evaluate(self.env)
        self.assertFalse(self.env.lookup_template(uri))

        self.env._template_table[uri] = template.as_triples(self.env)

        self.assertEqual(self.env.lookup_template(uri),
                         template.as_triples(self.env))
