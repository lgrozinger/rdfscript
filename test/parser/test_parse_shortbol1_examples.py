import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex

import rdfscript.parser as parser
import rdfscript.reader as reader

from rdfscript.toplevel import (TripleObject,
                                ConstructorDef,
                                Assignment,
                                InstanceExp)

from rdfscript.identifier import URI, QName, LocalName

from rdfscript.literal import Literal

from rdfscript.pragma import (ImportPragma,
                              PrefixPragma,
                              DefaultPrefixPragma)

class ParseShortBOL1ExamplesTest(unittest.TestCase):

    def setUp(self):
        self.parser = yacc.yacc(module=parser)
        self.reader = leex.lex(module=reader)
        self.reader.at_line_start = True
        self.reader.indent_stack = [0]
        self.log = logging.getLogger()

        ## types of toplevel AST node
        self.instanceexp_type = type(InstanceExp('', '', 0))
        self.prefix_type = type(PrefixPragma('', '', 0))
        self.import_type = type(ImportPragma('', 0))
        self.defaultprefix_type = type(DefaultPrefixPragma('', 0))
        self.assignment_type = type(Assignment('', '', 0))
        self.constructordef_type = type(ConstructorDef('', '', 0))

    def tearDown(self):
        None

    ## these tests only test success or failure of the parser, not
    ## that the AST is correct
    def test_parse_rdf_sbol_file(self):
        with open("test/parser/example-files/rdf.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])

    def test_parse_owl_sbol_file(self):
        with open("test/parser/example-files/owl.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        # import_type = type(ImportPragma('', 0))
        # assignment_type = type(Assignment('', '', 0))
        # self.instanceexp_type = type(InstanceExp('', '', 0))

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])

    def test_parse_biopax_sbol_file(self):
        with open("test/parser/example-files/biopax.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])

    def test_parse_chebi_sbol_file(self):
        with open("test/parser/example-files/chebi.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])


    def test_parse_dublin_core_sbol_file(self):
        with open("test/parser/example-files/dc.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])

    def test_parse_edam_sbol_file(self):
        with open("test/parser/example-files/edam.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])

    def test_parse_prov_sbol_file(self):
        with open("test/parser/example-files/prov.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type] +
                                    ([self.instanceexp_type] * 3))

    def test_parse_sbo_sbol_file(self):
        with open("test/parser/example-files/sbo.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])

    def test_parse_sbol_sbol_file(self):
        with open("test/parser/example-files/sbol.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type,
                         ([self.import_type] * 10) +
                         [self.prefix_type, self.defaultprefix_type] +
                         ([self.import_type] * 5))

    def test_parse_so_sbol_file(self):
        with open("test/parser/example-files/so.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])

    @unittest.skip("Do not understand this file (xml.sbol)")
    def test_parse_xml_sbol_file(self):
        with open("test/parser/example-files/xml.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.instanceexp_type] +
                                    ([self.import_type] * 3))

    def test_parse_xmlns_sbol_file(self):
        with open("test/parser/example-files/xmlns.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.instanceexp_type])

    def test_parse_xsd_sbol_file(self):
        with open("test/parser/example-files/xsd.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.prefix_type])

    @unittest.skip("Contains multi-line strings, not yet implemented.")
    def test_parse_component_sbol_file(self):
        with open("test/parser/example-files/sbol/component.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.instanceexp_type] * 23)

    def test_parse_core_sbol_file(self):
        with open("test/parser/example-files/sbol/core.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, ([self.assignment_type] * 2) +
                                    ([self.instanceexp_type] * 3))

    def test_parse_genomic_sbol_file(self):
        with open("test/parser/example-files/sbol/genomic.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type,
                         ([self.prefix_type] * 2) +
                         ([self.assignment_type] * 4) +
                         ([self.instanceexp_type] * 4) +
                         ([self.assignment_type] * 5) +
                         ([self.instanceexp_type] * 6) +
                         ([self.assignment_type] * 9) +
                         ([self.instanceexp_type] * 11) +
                         ([self.constructordef_type] * 29))

    def test_parse_genomic_generics_sbol_file(self):
        with open("test/parser/example-files/sbol/genomic_generics.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type,
                         [self.import_type] +
                         ([self.instanceexp_type] * 9))

    def test_parse_model_sbol_file(self):
        with open("test/parser/example-files/sbol/model.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type,
                         ([self.prefix_type] * 2) +
                         ([self.assignment_type] * 5))

    def test_parse_module_sbol_file(self):
        with open("test/parser/example-files/sbol/module.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type, [self.instanceexp_type] * 16)

    def test_parse_modules_sbol_file(self):
        with open("test/parser/example-files/sbol/modules.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        form_type = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(form_type,
                         ([self.prefix_type] * 2) +
                         ([self.assignment_type] * 16) +
                         ([self.constructordef_type] * 4))

if __name__ == '__main__':
    unittest.main()
