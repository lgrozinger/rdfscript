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

import test.test_helper as test

class ParserTemplateTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()
        self.maxDiff = None
        self.logger = logging.getLogger(__name__)

    def tearDown(self):
        None

    def test_template_noargs_nobase(self):
        script = 'DNASequence() =>\n  encoding = <SBOL:IUPACDNA>'
        forms  = self.parser.parse(script)

        expected_template = Template(test.name('DNASequence'),
                                     [],
                                     [Property(test.name('encoding'),
                                               Uri('SBOL:IUPACDNA', None),
                                               None)],
                                     None,
                                     None)


        self.assertEqual(forms, [expected_template])


    def test_template_onearg_nobase(self):
        script = 'DNASequence(x) =>\n  encoding = <SBOL:IUPACDNA>'
        forms  = self.parser.parse(script)

        expected_template = Template(test.name('DNASequence'),
                                     [test.name('x')],
                                     [Property(test.name('encoding'),
                                               Uri('SBOL:IUPACDNA', None),
                                               None)],
                                     None,
                                     None)


        self.assertEqual(forms, [expected_template])

    def test_template_multiargs_nobase(self):
        script = 'DNASequence(x, y, z) =>\n  encoding = <SBOL:IUPACDNA>'
        forms  = self.parser.parse(script)

        expected_template = Template(test.name('DNASequence'),
                                     [ test.name('x'),
                                       test.name('y'),
                                       test.name('z')],
                                     [Property(test.name('encoding'),
                                               Uri('SBOL:IUPACDNA', None),
                                               None)],
                                     None,
                                     None)


        self.assertEqual(forms, [expected_template])

    def test_template_onearg_base(self):
        script = 'B(x) =>\n  x = 42\nA(x) => B(x)\n  encoding = <SBOL:IUPACDNA>'
        forms  = self.parser.parse(script)

        expected_template = Template(test.name('A'),
                                     [test.name('x')],
                                     [Property(test.name('encoding'),
                                                         Uri('SBOL:IUPACDNA', None),
                                                         None)],
                                     Expansion(test.name('A'),
                                               test.name('B'),
                                               [test.name('x')],
                                               [],
                                               None),
                                     None)


        self.assertEqual([forms[1]], [expected_template])

if __name__ == '__main__':
    unittest.main()
