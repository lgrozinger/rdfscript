import unittest
import logging

from rdfscript.rdfscriptparser import RDFScriptParser

from rdfscript.pragma import ExtensionPragma
from rdfscript.core import Name, Uri, Value
from rdfscript.template import (Template,
                                Property)


class ParserTemplateTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()
        self.maxDiff = None
        self.logger = logging.getLogger(__name__)

    def tearDown(self):
        None

    def test_template_noargs_nobase(self):
        script = 'DNASequence()(encoding = <SBOL:IUPACDNA>)'
        forms = self.parser.parse(script)

        expected_template = Template(Name('DNASequence'),
                                     [],
                                     [Property(Name('encoding'),
                                               Name(Uri('SBOL:IUPACDNA')))],
                                     None,
                                     [])

        self.assertEqual(forms, [expected_template])

    def test_empty_template_noargs_nobase(self):
        script = 'DNASequence()'
        forms = self.parser.parse(script)

        expected_template = Template(Name('DNASequence'),
                                     [],
                                     [],
                                     None,
                                     [])

        self.assertEqual(forms, [expected_template])

    def test_empty_template_noargs(self):
        script = 'DNASequence() from Other()'
        forms = self.parser.parse(script)

        expected_template = Template(Name('DNASequence'),
                                     [],
                                     [],
                                     Name('Other'),
                                     [])

        self.assertEqual(forms, [expected_template])

    def test_empty_template_args(self):
        script = 'DNASequence(x, y, z) from Other(x)'
        forms = self.parser.parse(script)

        expected_template = Template(Name('DNASequence'),
                                     [Name('x'), Name('y'), Name('z')],
                                     [],
                                     Name('Other'),
                                     [Name('x')])

        self.assertEqual(forms, [expected_template])

    def test_empty_template_args_nobase(self):
        script = 'DNASequence(x, y, z)'
        forms = self.parser.parse(script)

        expected_template = Template(Name('DNASequence'),
                                     [Name('x'), Name('y'), Name('z')],
                                     [],
                                     None,
                                     [])

        self.assertEqual(forms, [expected_template])

    def test_template_onearg_nobase(self):
        script = 'DNASequence(x)(encoding = <SBOL:IUPACDNA>)'
        forms = self.parser.parse(script)

        expected_template = Template(Name('DNASequence'),
                                     [Name('x')],
                                     [Property(Name('encoding'),
                                               Name(Uri('SBOL:IUPACDNA')))],
                                     None,
                                     [])

        self.assertEqual(forms, [expected_template])

    def test_template_multiargs_nobase(self):
        script = 'DNASequence(x, y, z)(encoding = <SBOL:IUPACDNA>)'
        forms = self.parser.parse(script)

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
        forms = self.parser.parse(script)

        expected_template = Template(Name('A'),
                                     [Name('x')],
                                     [Property(Name('encoding'),
                                               Name(Uri('SBOL:IUPACDNA')))],
                                     Name('B'),
                                     [Name('x')])

        self.assertEqual([forms[1]], [expected_template])

    def test_expansion_in_property(self):
        script = 'A()(x = e is a B())'
        forms = self.parser.parse(script)

        e = self.parser.parse('e is a B()')[0]

        expected_template = Template(Name('A'),
                                     [],
                                     [Property(Name('x'), e)],
                                     None,
                                     [])

        self.assertEqual(expected_template, forms[0])

    def test_expansion_in_property_with_body(self):
        script = 'A()(x = e is a B()(y = 12345))'
        forms = self.parser.parse(script)

        e = self.parser.parse('e is a B()(y = 12345)')[0]

        expected_template = Template(Name('A'),
                                     [],
                                     [Property(Name('x'), e)],
                                     None,
                                     [])

        self.assertEqual(expected_template, forms[0])

    def test_expansion_in_body_with_body(self):
        script = 'A()(e is a B()(y = 12345))'
        forms = self.parser.parse(script)

        e = self.parser.parse('e is a B()(y = 12345)')[0]

        expected_template = Template(Name('A'),
                                     [],
                                     [e],
                                     None,
                                     [])

        self.assertEqual(expected_template, forms[0])

    def test_expansion_in_body(self):
        script = 'A()(e is a B())'
        forms = self.parser.parse(script)

        e = self.parser.parse('e is a B()')[0]

        expected_template = Template(Name('A'),
                                     [],
                                     [e],
                                     None,
                                     [])

        self.assertEqual(expected_template, forms[0])

    def test_expansion_in_property_with_args(self):
        script = 'A()(x = e is a B(12345))'
        forms = self.parser.parse(script)

        e = self.parser.parse('e is a B(12345)')[0]

        expected_template = Template(Name('A'),
                                     [],
                                     [Property(Name('x'), e)],
                                     None,
                                     [])

        self.assertEqual(expected_template, forms[0])

    def test_expansion_in_body_with_args(self):
        script = 'A()(e is a B(12345))'
        forms = self.parser.parse(script)

        e = self.parser.parse('e is a B(12345)')[0]

        expected_template = Template(Name('A'),
                                     [],
                                     [e],
                                     None,
                                     [])

        self.assertEqual(expected_template, forms[0])

    def test_extension_in_body(self):
        script = 'A()(@extension ExtensionName())'
        forms = self.parser.parse(script)

        a = forms[0]

        expected_template = Template(Name('A'),
                                     [],
                                     [ExtensionPragma(Name('ExtensionName'),
                                                      [])],
                                     None,
                                     [])

        self.assertEqual(expected_template, a)

    def test_extension_in_body_with_arg(self):
        script = 'A()(@extension ExtensionName(12345))'
        forms = self.parser.parse(script)

        a = forms[0]

        expected_template = Template(Name('A'),
                                     [],
                                     [ExtensionPragma(Name('ExtensionName'),
                                                      [Value(12345)])],
                                     None,
                                     [])

        self.assertEqual(expected_template, a)

    def test_extension_in_body_with_multi_args(self):
        script = 'A()(@extension ExtensionName(12345, 67890))'
        forms = self.parser.parse(script)

        a = forms[0]

        expected_template = Template(Name('A'),
                                     [],
                                     [ExtensionPragma(Name('ExtensionName'),
                                                      [Value(12345),
                                                       Value(67890)])],
                                     None,
                                     [])

        self.assertEqual(expected_template, a)


if __name__ == '__main__':
    unittest.main()
