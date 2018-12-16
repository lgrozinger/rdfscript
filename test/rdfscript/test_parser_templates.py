import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex
import logging

from rdfscript.rdfscriptparser import RDFScriptParser

from rdfscript.core import Name, Value, Uri, Assignment
from rdfscript.template import (Template,
                                Parameter,
                                Property)

from rdfscript.expansion import Expansion

class ParserTemplateTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()
        self.maxDiff = None
        self.logger = logging.getLogger(__name__)

    def tearDown(self):
        None

    def test_template_noargs_nobase(self):
        script = 'DNASequence()(encoding = <SBOL:IUPACDNA>)'
        forms  = self.parser.parse(script)

        expected_template = Template(Name('DNASequence'),
                                     [],
                                     [Property(Name('encoding'),
                                               Name(Uri('SBOL:IUPACDNA')))],
                                     None,
                                     [])

        self.assertEqual(forms, [expected_template])

    def test_empty_template_noargs_nobase(self):
        script = 'DNASequence()'
        forms  = self.parser.parse(script)

        expected_template = Template(Name('DNASequence'),
                                     [],
                                     [],
                                     None,
                                     [])

        self.assertEqual(forms, [expected_template])

    def test_empty_template_noargs(self):
        script = 'DNASequence() from Other()'
        forms  = self.parser.parse(script)

        expected_template = Template(Name('DNASequence'),
                                     [],
                                     [],
                                     Name('Other'),
                                     [])

        self.assertEqual(forms, [expected_template])

    def test_empty_template_args(self):
        script = 'DNASequence(x, y, z) from Other(x)'
        forms  = self.parser.parse(script)

        expected_template = Template(Name('DNASequence'),
                                     [Name('x'), Name('y'), Name('z')],
                                     [],
                                     Name('Other'),
                                     [Name('x')])

        self.assertEqual(forms, [expected_template])

    def test_empty_template_args_nobase(self):
        script = 'DNASequence(x, y, z)'
        forms  = self.parser.parse(script)

        expected_template = Template(Name('DNASequence'),
                                     [Name('x'), Name('y'), Name('z')],
                                     [],
                                     None,
                                     [])

        self.assertEqual(forms, [expected_template])


    def test_template_onearg_nobase(self):
        script = 'DNASequence(x)(encoding = <SBOL:IUPACDNA>)'
        forms  = self.parser.parse(script)

        expected_template = Template(Name('DNASequence'),
                                     [Name('x')],
                                     [Property(Name('encoding'),
                                               Name(Uri('SBOL:IUPACDNA')))],
                                     None,
                                     [])

        self.assertEqual(forms, [expected_template])

    def test_template_multiargs_nobase(self):
        script = 'DNASequence(x, y, z)(encoding = <SBOL:IUPACDNA>)'
        forms  = self.parser.parse(script)

        expected_template = Template(Name('DNASequence'),
                                     [Name('x'),
                                      Name('y'),
                                      Name('z')],
                                     [Property(Name('encoding'),
                                               Name(Uri('SBOL:IUPACDNA')))],
                                     None,
                                     [])

        self.assertEqual(forms, [expected_template])

    def test_template_onearg_base(self):
        script = 'B(x)(x = 42)\nA(x) from B(x)(encoding = <SBOL:IUPACDNA>)'
        forms  = self.parser.parse(script)

        expected_template = Template(Name('A'),
                                     [Name('x')],
                                     [Property(Name('encoding'),
                                               Name(Uri('SBOL:IUPACDNA')))],
                                     Name('B'),
                                     [Name('x')])

        self.assertEqual([forms[1]], [expected_template])

if __name__ == '__main__':
    unittest.main()
