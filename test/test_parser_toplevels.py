import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex

import rdfscript.parser as parser
import rdfscript.reader as reader

from rdfscript.toplevel import TripleObject, Assignment
from rdfscript.identifier import URI, QName, NSPrefix, LocalName
from rdfscript.literal import Literal

class ParserTopLevelTest(unittest.TestCase):

    def setUp(self):
        self.parser = yacc.yacc(module=parser)
        self.reader = leex.lex(module=reader)
        self.reader.at_line_start = True
        self.reader.indent_stack = [0]

    def tearDown(self):
        None

    def test_assignment(self):
        script = 'Identifier = "hello"'
        forms  = self.parser.parse(script, lexer=self.reader)

        self.assertEqual(forms,
                         [Assignment(QName(None, LocalName('Identifier', 1), 1),
                                     Literal("hello", 1),
                                     1)])

if __name__ == '__main__':
    unittest.main()
