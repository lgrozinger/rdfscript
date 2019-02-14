import unittest

import rdfscript.rdfscriptparser as parser
import rdfscript.templates as templates
import rdfscript.core as core


class ParserTemplateTest(unittest.TestCase):

    def setUp(self):
        self.parser = parser.RDFScriptParser()

    def tearDown(self):
        None

    def test_parser_triple_template(self):
        forms = self.parser.parse('Triple(a, b, c)(a > b > c)')

        triple = core.Name('Triple')
        a = core.Name('a')
        b = core.Name('b')
        c = core.Name('c')
        three = core.Three(a, b, c)
        template = templates.Template(triple, [a, b, c], [three])

        expected = [template]
        actually = forms
        self.assertEqual(expected, actually)

        #     def test_template_noargs_nobase(self):
        #         script = 'DNASequence()(encoding = <SBOL:IUPACDNA>)'
        #         forms = self.parser.parse(script)

        #         expected_template = Template(Name('DNASequence'),
        #                                      [],
        #                                      [Property(Name('encoding'),
        #                                                Name(Uri('SBOL:IUPACDNA')))])

        #         self.assertEqual(forms, [expected_template])

        #     def test_empty_template_noargs_nobase(self):
        #         script = 'DNASequence()'
        #         forms = self.parser.parse(script)

        #         expected_template = Template(Name('DNASequence'), [], [])

        #         self.assertEqual(forms, [expected_template])

        #     def test_empty_template_noargs(self):
        #         script = 'DNASequence()(Other())'
        #         forms = self.parser.parse(script)

        #         expected_template = Template(Name('DNASequence'),
        #                                      [],
        #                                      [Expansion(None, Name('Other'), [], [])])

        #         self.assertEqual(forms, [expected_template])

        #     def test_empty_template_args(self):
        #         script = 'DNASequence(x, y, z)(Other(x))'
        #         forms = self.parser.parse(script)

        #         expected_template = Template(Name('DNASequence'),
        #                                      [Name('x'), Name('y'), Name('z')],
        #                                      [Expansion(None, Name('Other'), [Name('x')], [])])

        #         self.assertEqual(forms, [expected_template])

        #     def test_empty_template_args_nobase(self):
        #         script = 'DNASequence(x, y, z)'
        #         forms = self.parser.parse(script)

        #         expected_template = Template(Name('DNASequence'),
        #                                      [Name('x'), Name('y'), Name('z')],
        #                                      [])

        #         self.assertEqual(forms, [expected_template])

        #     def test_template_onearg_nobase(self):
        #         script = 'DNASequence(x)(encoding = <SBOL:IUPACDNA>)'
        #         forms = self.parser.parse(script)

        #         expected_template = Template(Name('DNASequence'),
        #                                      [Name('x')],
        #                                      [Property(Name('encoding'),
        #                                                Name(Uri('SBOL:IUPACDNA')))])

        #         self.assertEqual(forms, [expected_template])

        #     def test_template_multiargs_nobase(self):
        #         script = 'DNASequence(x, y, z)(encoding = <SBOL:IUPACDNA>)'
        #         forms = self.parser.parse(script)

        #         expected_template = Template(Name('DNASequence'),
        #                                      [Name('x'),
        #                                       Name('y'),
        #                                       Name('z')],
        #                                      [Property(Name('encoding'),
        #                                                Name(Uri('SBOL:IUPACDNA')))])

        #         self.assertEqual(forms, [expected_template])

        #     def test_template_onearg_base(self):
        #         script = 'B(x)(x = 42)\nA(x)(B(x) encoding = <SBOL:IUPACDNA>)'
        #         forms = self.parser.parse(script)

        #         expected_template = Template(Name('A'),
        #                                      [Name('x')],
        #                                      [Expansion(None, Name('B'), [Name('x')], []),
        #                                       Property(Name('encoding'),
        #                                                Name(Uri('SBOL:IUPACDNA')))])

        #         self.assertEqual([forms[1]], [expected_template])

        #     def test_expansion_in_property(self):
        #         script = 'A()(x = e = B())'
        #         forms = self.parser.parse(script)

        #         e = self.parser.parse('e = B()')[0]

        #         expected_template = Template(Name('A'),
        #                                      [],
        #                                      [Property(Name('x'), e)])

        #         self.assertEqual(expected_template, forms[0])

        #     def test_expansion_in_property_with_body(self):
        #         script = 'A()(x = e = B()(y = 12345))'
        #         forms = self.parser.parse(script)

        #         e = self.parser.parse('e = B()(y = 12345)')[0]

        #         expected_template = Template(Name('A'),
        #                                      [],
        #                                      [Property(Name('x'), e)])

        #         self.assertEqual(expected_template, forms[0])

        #     def test_expansion_in_body_with_body(self):
        #         script = 'A()(e = B()(y = 12345))'
        #         forms = self.parser.parse(script)

        #         e = self.parser.parse('e = B()(y = 12345)')[0]

        #         expected_template = Template(Name('A'),
        #                                      [],
        #                                      [e])

        #         self.assertEqual(expected_template, forms[0])

        #     def test_expansion_in_body(self):
        #         script = 'A()(e = B())'
        #         forms = self.parser.parse(script)

        #         e = self.parser.parse('e = B()')[0]

        #         expected_template = Template(Name('A'),
        #                                      [],
        #                                      [e])

        #         self.assertEqual(expected_template, forms[0])

        #     def test_expansion_in_property_with_args(self):
        #         script = 'A()(x = e = B(12345))'
        #         forms = self.parser.parse(script)

        #         e = self.parser.parse('e = B(12345)')[0]

        #         expected_template = Template(Name('A'),
        #                                      [],
        #                                      [Property(Name('x'), e)])

        #         self.assertEqual(expected_template, forms[0])

        #     def test_expansion_in_body_with_args(self):
        #         script = 'A()(e = B(12345))'
        #         forms = self.parser.parse(script)

        #         e = self.parser.parse('e = B(12345)')[0]

        #         expected_template = Template(Name('A'),
        #                                      [],
        #                                      [e])

        #         self.assertEqual(expected_template, forms[0])

        #     def test_extension_in_body(self):
        #         script = 'A()(@extension ExtensionName())'
        #         forms = self.parser.parse(script)

        #         a = forms[0]

        #         expected_template = Template(Name('A'),
        #                                      [],
        #                                      [ExtensionPragma('ExtensionName', [])])

        #         self.assertEqual(expected_template, a)

        #     def test_extension_in_body_with_arg(self):
        #         script = 'A()(@extension ExtensionName(12345))'
        #         forms = self.parser.parse(script)

        #         a = forms[0]

        #         expected_template = Template(Name('A'),
        #                                      [],
        #                                      [ExtensionPragma('ExtensionName', [Value(12345)])])

        #         self.assertEqual(expected_template, a)

        #     def test_extension_in_body_with_multi_args(self):
        #         script = 'A()(@extension ExtensionName(12345, 67890))'
        #         forms = self.parser.parse(script)

        #         a = forms[0]

        #         expected_template = Template(Name('A'),
        #                                      [],
        #                                      [ExtensionPragma('ExtensionName',
        #                                                       [Value(12345),
        #                                                        Value(67890)])])

        #         self.assertEqual(expected_template, a)

        # if __name__ == '__main__':
        #     unittest.main()
