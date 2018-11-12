import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex

from rdfscript.rdfscriptparser import RDFScriptParser

from rdfscript.pragma import PrefixPragma
from rdfscript.core import Uri


class ParserPragmaTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    def test_parser_prefix_pragma(self):
        script = "@prefix Prefix <http://example.eg/>"
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [PrefixPragma('Prefix',
                                       Uri('http://example.eg/', None),
                                       None)])

if __name__ == '__main__':
    unittest.main()
