import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex
import rdflib

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from rdfscript.core import (Name,
                            Uri,
                            Value,
                            LocalName,
                            Prefix)
from rdfscript.pragma import (PrefixPragma,
                              DefaultPrefixPragma,
                              ImportPragma)

from rdfscript.evaluate import evaluate

import test.test_helper as test

class PragmaEvaluateTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()
        self.env = Env()

    def tearDown(self):
        None

    def test_prefix_pragma_name(self):

        uri = Uri('http://prefix.test/', None)
        name = test.name('uri')
        pragma = PrefixPragma(Prefix('test', None), test.name('uri'), None)
        self.env.assign(evaluate(name, self.env), evaluate(uri, self.env))

        self.assertEqual(evaluate(pragma, self.env), Prefix('test', None))
        self.assertEqual(self.env.uri_for_prefix(Prefix('test', None)), uri)

    def test_prefix_pragma_uri(self):

        uri = Uri('http://prefix.test/', None)
        pragma = PrefixPragma(Prefix('test', None), uri, None)

        self.assertEqual(evaluate(pragma, self.env), Prefix('test', None))
        self.assertEqual(self.env.uri_for_prefix(Prefix('test', None)), uri)

    def test_default_prefix_pragma(self):

        prefix = Prefix('test', None)
        uri = Uri('http://prefix.test/', None)
        self.env.bind_prefix(prefix, uri)
        self.assertNotEqual(self.env.default_prefix, prefix)

        pragma = DefaultPrefixPragma(prefix, None)
        self.assertEqual(evaluate(pragma, self.env), prefix)
        self.assertEqual(self.env.default_prefix, prefix)
