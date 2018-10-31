import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex
import logging

import rdfscript.parser as parser
import rdfscript.reader as reader

from rdfscript.toplevel import TripleObject, Assignment, ConstructorDef
from rdfscript.identifier import URI, QName, LocalName
from rdfscript.literal import Literal

class ParserTopLevelTest(unittest.TestCase):

    def setUp(self):
        self.parser = yacc.yacc(module=parser)
        self.reader = leex.lex(module=reader)
        self.reader.at_line_start = True
        self.reader.indent_stack = [0]
        self.log = logging.getLogger()

    def tearDown(self):
        None

    def test_assignment(self):
        script = 'Identifier = "hello"'
        forms  = self.parser.parse(script, lexer=self.reader, debug=self.log)

        self.assertEqual(forms,
                         [Assignment(LocalName('Identifier', 1),
                                     Literal("hello", 1),
                                     1)])

    def test_constructordef_onearg(self):
        script = 'DNASequence(x) => Sequence\n  encoding = <SBOL:IUPACDNA>\n  elements = x\n'
        forms  = self.parser.parse(script, lexer=self.reader, debug=self.log)

        self.assertEqual(forms,
                         [ConstructorDef(LocalName('DNASequence', 1),
                                         [LocalName('x', 1)], 1)])


if __name__ == '__main__':
    unittest.main()
