import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex
import logging

from rdfscript.rdfscriptparser import RDFScriptParser

from rdfscript.core import Name, Value
from rdfscript.templating import Assignment

class ParserTopLevelTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    def test_assignment(self):
        script = 'Identifier = "hello"'
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [Assignment(Name(None, 'Identifier', None),
                                     Value("hello", None),
                                     None)])

    @unittest.skip("Templates not implemented yet.")
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
