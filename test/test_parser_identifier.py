import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex

import rdfscript.parser as parser
import rdfscript.reader as reader

from rdfscript.toplevel import TripleObject
from rdfscript.identifier import URI, QName, LocalName
from rdfscript.literal import Literal

class ParserIdentifierTest(unittest.TestCase):

    def setUp(self):
        self.parser = yacc.yacc(module=parser)
        self.reader = leex.lex(module=reader)
        self.reader.at_line_start = True
        self.reader.indent_stack = [0]

    def tearDown(self):
        None

    def test_parser_uri(self):
        script = "<http://uri.org/>"
        forms  = self.parser.parse(script, lexer=self.reader)

        self.assertEqual(forms, [URI('http://uri.org/', 1)])

    def test_parser_qname(self):
        script = 'Prefix:LocalName'
        forms = self.parser.parse(script, lexer=self.reader)

        prefix = 'Prefix'
        localname = 'LocalName'

        self.assertEqual(forms, [QName(prefix, localname, 1)])

    def test_parser_localname(self):
        script = 'localName'
        forms = self.parser.parse(script, lexer=self.reader)

        self.assertEqual(forms, [LocalName('localName', 1)])


if __name__ == '__main__':
    unittest.main()
