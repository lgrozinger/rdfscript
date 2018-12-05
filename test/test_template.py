import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex
import rdflib

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from rdfscript.core import (Name,
                            Value,
                            Uri,
                            Prefix,
                            LocalName)

from rdfscript.template import (Template,
                                Expansion,
                                Parameter,
                                Argument,
                                Property)
from rdfscript.pragma import ExtensionPragma
import test.test_helper as test

class TemplateClassTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()
        self.parser = RDFScriptParser()
        self.maxDiff = None
        self.env.bind_prefix(Prefix('otherprefix', None), Uri('http://otherprefix/', None))

        self.template = Template(test.name('T'),
                                 [test.name('a'),
                                  test.name('b')],
                                 [test.property(test.name('a'), test.name('value')),
                                  test.property(test.name('predicate'), test.name('b')),
                                  test.property(test.name('expansion'),
                                                Expansion(test.name('exp', p='otherprefix'),
                                                          test.name('a'),
                                                          [test.name('b')],
                                                          [],
                                                     None))],
                                 None,
                                 None)

        self.simple_template = Template(test.name('T'),
                                 [test.name('a'),
                                  test.name('b')],
                                 [Property(test.name('a'),
                                           test.name('value'),
                                           None),
                                  Property(test.name('predicate'),
                                           test.name('b'),
                                           None)],
                                 None,
                                 None)

        self.specialised = Template(test.name('S'),
                                    [test.name('x')],
                                    [],
                                    Expansion(test.name('S'),
                                              test.name('T'),
                                              [test.name('x'),
                                               Value(1, None)],
                                              [],
                                              None),
                                    None)

    def tearDown(self):
        None

    def test_de_name(self):

        self.template.parameterise()

        self.env.bind_prefix(Prefix('test_template', None), Uri('http://test_template/', None))
        self.env.set_default_prefix(Prefix('test_template', None))

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

    @unittest.skip("Bind params not in use.")
    def test_bind_params(self):

        self.template.parameterise()

        args = [Argument(Value(42, None), 0, None),
                Argument(Uri('http://arg.org/', None), 1, None)]

        self.assertEqual(self.template.name, test.name('T'))

        self.assertEqual(self.template.parameters, [Parameter('a', 0, None),
                                               Parameter('b', 1, None)])

        self.assertEqual(self.template.body[0], Property(Value(42, None),
                                                         test.name('value'),
                                                         None))

        self.assertEqual(self.template.body[1], Property(test.name('predicate'),
                                                    Uri('http://arg.org/', None),
                                                    None))

        self.assertEqual(self.template.body[2].name, test.name('expansion'))

        self.assertEqual(self.template.body[2].value.name, test.name('exp', p='otherprefix'))

        self.assertEqual(self.template.body[2].value.template, Value(42, None))

        self.assertEqual(self.template.body[2].value.args, [Argument(Uri('http://arg.org/', None),
                                                                0,
                                                                None)])

        self.assertEqual(self.template.body[2].value.body, [])

        self.assertEqual(len(self.template.body), 3)

    def test_sub_params(self):

        self.template.parameterise()

        self.assertEqual(self.template.name, test.name('T'))

        self.assertEqual(self.template.parameters, [Parameter('a', 0, None),
                                                    Parameter('b', 1, None)])

        self.assertEqual(self.template.body[0], Property(Parameter('a', 0, None),
                                                         test.name('value'),
                                                         None))

        self.assertEqual(self.template.body[1], Property(test.name('predicate'),
                                                         Parameter('b', 1, None),
                                                         None))

        self.assertEqual(self.template.body[2].name, test.name('expansion'))

        self.assertEqual(self.template.body[2].value.name, test.name('exp', p='otherprefix'))

        self.assertEqual(self.template.body[2].value.template, Parameter('a', 0, None))

        self.assertEqual(self.template.body[2].value.args, [Argument(Parameter('b', 1, None),
                                                                     0,
                                                                     None)])

        self.assertEqual(self.template.body[2].value.body, [])

        self.assertEqual(len(self.template.body), 3)

    def test_derived_forward_parameters(self):

        self.template.parameterise()
        self.template.de_name(self.env)
        self.specialised.parameterise()

        self.assertEqual(self.specialised.base.args[0], Argument(Parameter('x', 0, None), 0, None))

