import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex
import logging

from rdfscript.rdfscriptparser import RDFScriptParser

from rdfscript.toplevel import TripleObject, Assignment, ConstructorDef
from rdfscript.identifier import URI, QName, LocalName
from rdfscript.literal import Literal

class ParserTopLevelTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    def test_assignment(self):
        script = 'Identifier = "hello"'
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [Assignment(LocalName('Identifier', 1),
                                     Literal("hello", 1),
                                     1)])

    def test_constructordef_onearg(self):
        script = 'DNASequence(x) => Sequence\n  encoding = <SBOL:IUPACDNA>'
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [ConstructorDef(LocalName('Sequence', 1),
                                         LocalName('DNASequence', 1),
                                         [LocalName('x', 1)],
                                         [Assignment(LocalName('encoding', 1),
                                                     URI('SBOL:IUPACDNA', 1),
                                                     1)],
                                         1)])

if __name__ == '__main__':
    unittest.main()
