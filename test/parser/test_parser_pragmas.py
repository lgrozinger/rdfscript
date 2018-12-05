import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex

from rdfscript.rdfscriptparser import RDFScriptParser

from rdfscript.pragma import (PrefixPragma,
                              DefaultPrefixPragma,
                              ImportPragma)

from rdfscript.core import Uri, Prefix

import test.test_helper as test

class ParserPragmaTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    def test_prefix_pragma_uri(self):
        script = "@prefix Prefix <http://example.eg/>"
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [PrefixPragma(Prefix('Prefix', None),
                                       Uri('http://example.eg/', None),
                                       None)])

    def test_prefix_pragma_name(self):
        script = "@prefix Prefix name"
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [PrefixPragma(Prefix('Prefix', None),
                                       test.name('name'),
                                       None)])

    def test_default_prefix_pragma(self):
        script = "@defaultPrefix Prefix"
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [DefaultPrefixPragma(Prefix('Prefix', None), None)])

    def test_import_pragma_uri(self):
        script = "@import <import>"
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [ImportPragma(Uri('import', None), None)])

        script = "import <import>"
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [ImportPragma(Uri('import', None), None)])

    def test_import_pragma_name(self):
        script = "@import this.target"
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [ImportPragma(test.name('target', p='this'), None)])

        script = "import this.target"
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [ImportPragma(test.name('target', p='this'), None)])

if __name__ == '__main__':
    unittest.main()
