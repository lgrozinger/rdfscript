import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex
import rdflib

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from rdfscript.core import (Name,
                            Value,
                            Uri)

from rdfscript.template import (Template,
                                Expansion,
                                Parameter,
                                Argument,
                                Property)
from rdfscript.pragma import ExtensionPragma


class TemplateClassTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()
        self.parser = RDFScriptParser()
        self.maxDiff = None

        self.template = Template(Name(None, 'T', None),
                                 [Name(None, 'a', None),
                                  Name(None, 'b', None)],
                                 [Property(Name(None, 'a', None),
                                           Name(None, 'value', None),
                                           None),
                                  Property(Name(None, 'predicate', None),
                                           Name(None, 'b', None),
                                           None),
                                  Property(Name(None, 'expansion', None),
                                           Expansion(Name('otherprefix', 'exp', None),
                                                     Name(None, 'a', None),
                                                     [Name(None, 'b', None)],
                                                     [],
                                                     None),
                                           None)],
                                 None,
                                 None)

    def tearDown(self):
        None

    def test_de_name(self):

        self.template.parameterise()

        self.env.bind_prefix('test_template', rdflib.URIRef('http://test_template/'))
        self.env.set_default_prefix('test_template')
        self.env.bind_prefix('otherprefix', rdflib.URIRef('http://otherprefix/'))

        self.template.de_name(self.env)

        self.assertEqual(self.template.name, Uri('http://test_template/T', None))

        self.assertEqual(self.template.parameters, [Parameter('a', 0, None),
                                               Parameter('b', 1, None)])

        self.assertEqual(self.template.body[0], Property(Parameter('a', 0, None),
                                                     Uri('http://test_template/value', None),
                                                     None))

        self.assertEqual(self.template.body[1], Property(Uri('http://test_template/predicate', None),
                                                    Parameter('b', 1, None),
                                                    None))

        self.assertEqual(self.template.body[2].name, Uri('http://test_template/expansion', None))

        self.assertEqual(self.template.body[2].value.name, Uri('http://otherprefix/exp', None))

        self.assertEqual(self.template.body[2].value.template, Parameter('a', 0, None))

        self.assertEqual(self.template.body[2].value.args, [Argument(Parameter('b', 1, None),
                                                                0,
                                                                None)])

        self.assertEqual(self.template.body[2].value.body, [])

        self.assertEqual(len(self.template.body), 3)

    def test_bind_params(self):

        self.template.parameterise()

        args = [Argument(Value(42, None), 0, None),
                Argument(Uri('http://arg.org/', None), 1, None)]

        self.template.bind(args)

        self.assertEqual(self.template.name, Name(None, 'T', None))

        self.assertEqual(self.template.parameters, [Parameter('a', 0, None),
                                               Parameter('b', 1, None)])

        self.assertEqual(self.template.body[0], Property(Value(42, None),
                                                    Name(None, 'value', None),
                                                    None))

        self.assertEqual(self.template.body[1], Property(Name(None, 'predicate', None),
                                                    Uri('http://arg.org/', None),
                                                    None))

        self.assertEqual(self.template.body[2].name, Name(None, 'expansion', None))

        self.assertEqual(self.template.body[2].value.name, Name('otherprefix', 'exp', None))

        self.assertEqual(self.template.body[2].value.template, Value(42, None))

        self.assertEqual(self.template.body[2].value.args, [Argument(Uri('http://arg.org/', None),
                                                                0,
                                                                None)])

        self.assertEqual(self.template.body[2].value.body, [])

        self.assertEqual(len(self.template.body), 3)

    def test_sub_params(self):

        self.template.parameterise()

        self.assertEqual(self.template.name, Name(None, 'T', None))

        self.assertEqual(self.template.parameters, [Parameter('a', 0, None),
                                               Parameter('b', 1, None)])

        self.assertEqual(self.template.body[0], Property(Parameter('a', 0, None),
                                                     Name(None, 'value', None),
                                                     None))

        self.assertEqual(self.template.body[1], Property(Name(None, 'predicate', None),
                                                    Parameter('b', 1, None),
                                                    None))

        self.assertEqual(self.template.body[2].name, Name(None, 'expansion', None))

        self.assertEqual(self.template.body[2].value.name, Name('otherprefix', 'exp', None))

        self.assertEqual(self.template.body[2].value.template, Parameter('a', 0, None))

        self.assertEqual(self.template.body[2].value.args, [Argument(Parameter('b', 1, None),
                                                                0,
                                                                None)])

        self.assertEqual(self.template.body[2].value.body, [])

        self.assertEqual(len(self.template.body), 3)

