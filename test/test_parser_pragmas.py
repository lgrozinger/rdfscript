import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex

import rdfscript.parser as parser
import rdfscript.reader as reader

from rdfscript.pragma import PrefixPragma
from rdfscript.identifier import URI


class ParserPragmaTest(unittest.TestCase):

    def setUp(self):
        self.parser = yacc.yacc(module=parser)
        self.reader = leex.lex(module=reader)
        self.reader.at_line_start = True
        self.reader.indent_stack = [0]

    def tearDown(self):
        None

    def test_parser_prefix_pragma(self):
        script = "@prefix Prefix <http://example.eg/>"
        forms  = self.parser.parse(script, lexer=self.reader)

        self.assertEqual(forms, [PrefixPragma('Prefix', URI('http://example.eg/', 1), 1)])

if __name__ == '__main__':
    unittest.main()
