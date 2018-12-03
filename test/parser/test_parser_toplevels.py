import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex
import logging

from rdfscript.rdfscriptparser import RDFScriptParser

from rdfscript.core import Name, Value, Uri
from rdfscript.templating import Assignment
from rdfscript.template import (Template,
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

    def test_template_noargs_nobase(self):
        script = 'DNASequence() =>\n  encoding = <SBOL:IUPACDNA>'
        forms  = self.parser.parse(script)

        expected_template = Template(Name(None, 'DNASequence', None),
                                     [],
                                     [Property(Name(None, 'encoding', None),
                                               Uri('SBOL:IUPACDNA', None),
                                               None)],
                                     None,
                                     None)


        self.assertEqual(forms, [expected_template])


    def test_template_onearg_nobase(self):
        script = 'DNASequence(x) =>\n  encoding = <SBOL:IUPACDNA>'
        forms  = self.parser.parse(script)

        expected_template = Template(Name(None, 'DNASequence', None),
                                     [Name(None, 'x', None)],
                                     [Property(Name(None, 'encoding', None),
                                               Uri('SBOL:IUPACDNA', None),
                                               None)],
                                     None,
                                     None)


        self.assertEqual(forms, [expected_template])

    def test_template_multiargs_nobase(self):
        script = 'DNASequence(x, y, z) =>\n  encoding = <SBOL:IUPACDNA>'
        forms  = self.parser.parse(script)

        expected_template = Template(Name(None, 'DNASequence', None),
                                     [Name(None, 'x', None),
                                      Name(None, 'y', None),
                                      Name(None, 'z', None)],
                                     [Property(Name(None, 'encoding', None),
                                               Uri('SBOL:IUPACDNA', None),
                                               None)],
                                     None,
                                     None)


        self.assertEqual(forms, [expected_template])

    def test_template_onearg_base(self):
        script = 'B(x) =>\n  x = 42\nA(x) => B(x)\n  encoding = <SBOL:IUPACDNA>'
        forms  = self.parser.parse(script)

        expected_template = Template(Name(None, 'A', None),
                                     [Name(None, 'x', None)],
                                     [Property(Name(None, 'encoding', None),
                                                         Uri('SBOL:IUPACDNA', None),
                                                         None)],
                                     Expansion(Name(None, 'A', None),
                                               Name(None, 'B', None),
                                               [Name(None, 'x', None)],
                                               [],
                                               None),
                                     None)


        self.assertEqual([forms[1]], [expected_template])

if __name__ == '__main__':
    unittest.main()
