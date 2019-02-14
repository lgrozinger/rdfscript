import unittest

import rdfscript.rdfscriptparser as parser
import rdfscript.core as core
import rdfscript.templates as templates
import rdfscript.expansions as expansions


class ParserExpansionTest(unittest.TestCase):

    def setUp(self):
        self.parser = parser.RDFScriptParser()

    def tearDown(self):
        None

    def test_expansion_no_args_no_body(self):

        forms = self.parser.parse('e = a()')
        expect = expansions.Expansion(core.Name('e'),
                                      core.Name('a'),
                                      [],
                                      [])

        self.assertEqual(expect, forms[0])

    def test_expansion_one_arg_no_body(self):

        forms = self.parser.parse('e = a(12345)')
        expect = expansions.Expansion(core.Name('e'),
                                      core.Name('a'),
                                      [core.Value(12345)],
                                      [])

        self.assertEqual(expect, forms[0])

    def test_expansion_multi_args_no_body(self):

        forms = self.parser.parse('e = a(12345, 54321)')
        expect = expansions.Expansion(core.Name('e'),
                                      core.Name('a'),
                                      [core.Value(12345),
                                       core.Value(54321)],
                                      [])

        self.assertEqual(expect, forms[0])

    def test_expansion_expansion_as_arg(self):

        forms = self.parser.parse('e = a(f = b(12345))')
        f = self.parser.parse('f = b(12345)')[0]
        expect = expansions.Expansion(core.Name('e'),
                                      core.Name('a'),
                                      [f],
                                      [])

        self.assertEqual(expect, forms[0])

    def test_expansion_no_args_with_body(self):

        forms = self.parser.parse('e = a()(x > y > z)')
        expect = expansions.Expansion(core.Name('e'),
                                      core.Name('a'),
                                      [],
                                      [core.Three(core.Name('x'),
                                                  core.Name('y'),
                                                  core.Name('z'))])

        self.assertEqual(expect, forms[0])

    def test_expansion_one_arg_with_body(self):

        forms = self.parser.parse('e = a(12345)(x > y > z)')
        expect = expansions.Expansion(core.Name('e'),
                                      core.Name('a'),
                                      [core.Value(12345)],
                                      [core.Three(core.Name('x'),
                                                  core.Name('y'),
                                                  core.Name('z'))])

        self.assertEqual(expect, forms[0])

    def test_expansion_multi_args_with_body(self):

        forms = self.parser.parse('e = a(12345, 54321)(x > y > z)')
        expect = expansions.Expansion(core.Name('e'),
                                      core.Name('a'),
                                      [core.Value(12345),
                                       core.Value(54321)],
                                      [core.Three(core.Name('x'),
                                                  core.Name('y'),
                                                  core.Name('z'))])

        self.assertEqual(expect, forms[0])

    @unittest.skip("Properties not implemented yet.")
    def test_expansion_multiple_properties(self):

        forms = self.parser.parse('e = a()(x=true y=false)')
        expect = expansions.Expansion(core.Name('e'),
                                      core.Name('a'),
                                      [],
                                      [templates.Property(core.Name('x'), core.Value(True)),
                                       templates.Property(core.Name('y'), core.Value(False))])

        self.assertEqual(expect, forms[0])
