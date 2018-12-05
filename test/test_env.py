import unittest
import logging

import rdflib

from rdfscript.env import Env
from rdfscript.core import (Name,
                            Value,
                            Uri,
                            Prefix,
                            LocalName)

from rdfscript.template import (Template,
                                Parameter,
                                Property)

from rdfscript.evaluate import evaluate
from rdfscript.error import PrefixError

class EnvTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()

    def tearDown(self):
        None

    def test_prefix_binding(self):

        prefix_uri = Uri('http://test.prefix.eg/', None)
        prefix = Prefix('x', None)

        self.env.bind_prefix(prefix, prefix_uri)

        name = Name(prefix, LocalName('local', None), None)
        resolved_uri = self.env.resolve_name(name)
        self.assertEqual(resolved_uri, Uri('http://test.prefix.eg/local', None))

    def test_get_and_set_default_prefix(self):

        prefix = Prefix('x', None)
        self.env.bind_prefix(prefix, Uri('http://eg/', None))
        before = Uri(self.env._rdf._g.identifier.toPython(), None)
        self.assertEqual(Prefix(before, None), self.env.default_prefix)

        self.env.set_default_prefix(prefix)
        self.assertEqual(prefix, self.env.default_prefix)

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
