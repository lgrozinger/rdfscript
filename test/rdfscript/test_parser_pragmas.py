import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex

from rdfscript.rdfscriptparser import RDFScriptParser

from rdfscript.pragma import (PrefixPragma,
                              DefaultPrefixPragma,
                              ImportPragma)

from rdfscript.core import Uri, Name

class ParserPragmaTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    @unittest.skip("Prefix pragma is dead.")
    def test_prefix_pragma_uri(self):
        script = "@prefix Prefix <http://example.eg/>"
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [PrefixPragma(Prefix('Prefix', None),
                                       Uri('http://example.eg/', None),
                                       None)])

    @unittest.skip("Prefix pragma is dead.")
    def test_prefix_pragma_name(self):
        script = "@prefix Prefix name"
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [PrefixPragma(Prefix('Prefix', None),
                                       test.name('name'),
                                       None)])

    @unittest.skip("Prefix pragma is dead.")
    def test_default_prefix_pragma(self):
        script = "@defaultPrefix Prefix"
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [DefaultPrefixPragma(Prefix('Prefix', None), None)])

    def test_import_pragma_uri(self):
        script = "@import <import>"
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [ImportPragma(Name(Uri('import')))])

        script = "import <import>"
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [ImportPragma(Name(Uri('import')))])

    def test_import_pragma_name(self):
        script = "@import this.target"
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [ImportPragma(Name('this', 'target'))])

        script = "import this.target"
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [ImportPragma(Name('this', 'target'))])

if __name__ == '__main__':
    unittest.main()
