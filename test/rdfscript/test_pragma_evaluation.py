import unittest

import pdb

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from rdfscript.core import (Name,
                            Uri,
                            Value)
from rdfscript.pragma import (PrefixPragma,
                              DefaultPrefixPragma,
                              ImportPragma)


class PragmaEvaluateTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()
        self.env = Env()

    def tearDown(self):
        None

    def test_prefix_pragma_name(self):

        uri = Uri('http://prefix.test/')
        name = Name('uri')
        pragma = PrefixPragma('test', Name('uri'))
        self.env.assign(name.evaluate(self.env), uri)
        value = pragma.evaluate(self.env)

        self.assertEqual(value, Name('test'))
        prefix = Uri(self.env.default_prefix)
        prefix.extend(Uri('test'), delimiter='')
        self.assertTrue(self.env._symbol_table.get(prefix, False))
        self.assertEqual(Name('test').evaluate(self.env), uri)
        self.assertEqual(self.env.lookup(prefix), uri)

    def test_prefix_pragma_uri(self):

        uri = Uri('http://prefix.test/')
        pragma = PrefixPragma('test', Name(uri))
        value = pragma.evaluate(self.env)

        self.assertEqual(value, Name('test'))
        prefix = Uri(self.env.default_prefix)
        prefix.extend(Uri('test'), delimiter='')
        self.assertTrue(self.env._symbol_table.get(prefix, False))
        self.assertEqual(Name('test').evaluate(self.env), uri)
        self.assertEqual(self.env.lookup(prefix), uri)

    def test_default_prefix_pragma(self):

        prefix = 'test'
        uri = Uri('http://prefix.test/')
        self.env.bind_prefix(prefix, uri)
        self.assertNotEqual(self.env.default_prefix, prefix)

        pragma = DefaultPrefixPragma(prefix)
        self.assertEqual(pragma.evaluate(self.env), Name(prefix))
        self.assertEqual(self.env.default_prefix, uri)

    def test_extension_pragma_evaluate_args(self):

        e = self.parser.parse('@extension E(arg)')[0]

        e.evaluate(self.env)

        self.assertEqual(e.args, [Name('arg').evaluate(self.env)])
