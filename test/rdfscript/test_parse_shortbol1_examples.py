import unittest

from rdfscript.rdfscriptparser import RDFScriptParser

from rdfscript.pragma import (PrefixPragma,
                              DefaultPrefixPragma,
                              ImportPragma)

from rdfscript.core import Assignment
from rdfscript.template import (Template,
                                Expansion)

@unittest.skip("ShortBOL2 syntax has diverged from ShortBOL1.")
class ParseShortBOL1ExamplesTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser(debug=True)

        ## types of toplevel AST node
        self.expansion_type = type(Expansion(None, None, [], [], None))
        self.prefix_type = type(PrefixPragma(None, None, None))
        self.import_type = type(ImportPragma(None, None))
        self.defaultprefix_type = type(DefaultPrefixPragma(None, None))
        self.assignment_type = type(Assignment(None, None, None))
        self.template_type = type(Template(None, [], [], None, None))

    def tearDown(self):
        None

    ## these tests only test success or failure of the parser, not
    ## that the AST is correct
    def test_parse_rdf_sbol_file(self):
        with open("test/parser/example-files/rdf.sbol", 'r') as in_file:
            data = in_file.read()

        forms = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])

    def test_parse_owl_sbol_file(self):
        with open("test/parser/example-files/owl.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        # import_type = type(ImportPragma('', 0))
        # assignment_type = type(Assignment('', '', 0))
        # self.expansion_type = type(Expansion('', '', 0))

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])

    def test_parse_biopax_sbol_file(self):
        with open("test/parser/example-files/biopax.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])

    def test_parse_chebi_sbol_file(self):
        with open("test/parser/example-files/chebi.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])


    def test_parse_dublin_core_sbol_file(self):
        with open("test/parser/example-files/dc.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])

    def test_parse_edam_sbol_file(self):
        with open("test/parser/example-files/edam.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])

    def test_parse_prov_sbol_file(self):
        with open("test/parser/example-files/prov.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type] +
                                    ([self.expansion_type] * 3))

    def test_parse_sbo_sbol_file(self):
        with open("test/parser/example-files/sbo.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])

    def test_parse_sbol_sbol_file(self):
        with open("test/parser/example-files/sbol.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type,
                         ([self.import_type] * 10) +
                         [self.prefix_type, self.defaultprefix_type] +
                         ([self.import_type] * 5))

    def test_parse_so_sbol_file(self):
        with open("test/parser/example-files/so.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])

    @unittest.skip("Even the ShortBOL1.0 sandbox cannot parse this file.")
    def test_parse_xml_sbol_file(self):
        with open("test/parser/example-files/xml.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.expansion_type] +
                                    ([self.import_type] * 3))

    def test_parse_xmlns_sbol_file(self):
        with open("test/parser/example-files/xmlns.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.expansion_type])

    def test_parse_xsd_sbol_file(self):
        with open("test/parser/example-files/xsd.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])

    @unittest.skip("Contains multi-line strings, not yet implemented.")
    def test_parse_component_sbol_file(self):
        with open("test/parser/example-files/sbol/component.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.expansion_type] * 23)

    def test_parse_core_sbol_file(self):
        with open("test/parser/example-files/sbol/core.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, ([self.assignment_type] * 2) +
                                    ([self.expansion_type] * 3))

    def test_parse_genomic_sbol_file(self):
        with open("test/parser/example-files/sbol/genomic.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type,
                         ([self.prefix_type] * 2) +
                         ([self.assignment_type] * 4) +
                         ([self.expansion_type] * 4) +
                         ([self.assignment_type] * 5) +
                         ([self.expansion_type] * 6) +
                         ([self.assignment_type] * 9) +
                         ([self.expansion_type] * 11) +
                         ([self.template_type] * 29))

    def test_parse_genomic_generics_sbol_file(self):
        with open("test/parser/example-files/sbol/genomic_generics.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type,
                         [self.import_type] +
                         ([self.expansion_type] * 9))

    def test_parse_model_sbol_file(self):
        with open("test/parser/example-files/sbol/model.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type,
                         ([self.prefix_type] * 2) +
                         ([self.assignment_type] * 5))

    def test_parse_module_sbol_file(self):
        with open("test/parser/example-files/sbol/module.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.expansion_type] * 16)

    def test_parse_modules_sbol_file(self):
        with open("test/parser/example-files/sbol/modules.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type,
                         ([self.prefix_type] * 2) +
                         ([self.assignment_type] * 16) +
                         ([self.template_type] * 4))

if __name__ == '__main__':
    unittest.main()
