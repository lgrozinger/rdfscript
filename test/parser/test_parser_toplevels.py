import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex
import logging

from rdfscript.rdfscriptparser import RDFScriptParser

from rdfscript.core import Name, Value, Uri
from rdfscript.templating import (Assignment,
                                  Template,
                                  Expansion,
                                  Parameter,
                                  Property)

class ParserTopLevelTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()
        self.maxDiff = None
        self.logger = logging.getLogger(__name__)

    def tearDown(self):
        None

    def test_assignment(self):
        script = 'Identifier = "hello"'
        forms  = self.parser.parse(script)

        self.assertEqual(forms,
                         [Assignment(Name(None, 'Identifier', None),
                                     Value("hello", None),
                                     None)])

    def test_template_def_noargs_nobase(self):
        script = 'DNASequence =>\n  encoding = <SBOL:IUPACDNA>'
        forms  = self.parser.parse(script)

        expected_template = Template(Name(None, 'DNASequence', None),
                                     [],
                                     [Property(Name(None, 'encoding', None),
                                               Uri('SBOL:IUPACDNA', None),
                                               None)],
                                     None,
                                     None)


        self.assertEqual(forms, [expected_template])


    def test_constructordef_onearg_nobase(self):
        script = 'DNASequence(x) =>\n  encoding = <SBOL:IUPACDNA>'
        forms  = self.parser.parse(script)

        expected_template = Template(Name(None, 'DNASequence', None),
                                     ['x'],
                                     [Property(Name(None, 'encoding', None),
                                               Uri('SBOL:IUPACDNA', None),
                                               None)],
                                     None,
                                     None)


        self.assertEqual(forms, [expected_template])

    def test_constructordef_multiargs_nobase(self):
        script = 'DNASequence(x, y, z) =>\n  encoding = <SBOL:IUPACDNA>'
        forms  = self.parser.parse(script)

        expected_template = Template(Name(None, 'DNASequence', None),
                                     ['x','y','z'],
                                     [Property(Name(None, 'encoding', None),
                                               Uri('SBOL:IUPACDNA', None),
                                               None)],
                                     None,
                                     None)


        self.assertEqual(forms, [expected_template])

    def test_constructordef_onearg_base(self):
        script = 'B(x) =>\n  x = 42\nA(x) => B(x)\n  encoding = <SBOL:IUPACDNA>'
        forms  = self.parser.parse(script)

        expected_template = Template(Name(None, 'A', None),
                                     ['x'],
                                     [Property(Name(None, 'encoding', None),
                                               Uri('SBOL:IUPACDNA', None),
                                               None)],
                                     None,
                                     Expansion(Name(None, 'B', None),
                                               Name(None, 'A', None),
                                               [Name(None, 'x', None)],
                                               [],
                                               None))


        self.assertEqual(forms[1], expected_template)
if __name__ == '__main__':
    unittest.main()
