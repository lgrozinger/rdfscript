import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex
import rdflib

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from rdfscript.core import (Name,
                            Uri,
                            Self,
                            Value)

from rdfscript.template import (Template,
                                Property)
from rdfscript.pragma import ExtensionPragma

from rdfscript.error import UnexpectedType

class TemplateClassTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    def test_init(self):

        template = Template(Name('x'), [], [], None)

        self.assertEqual(template.name, Name('x'))

    def test_check_param_not_name(self):

        name = Name('x')
        notname = Value(1)
        template = Template(Name('x'), [], [], None)

        with self.assertRaises(UnexpectedType):
            template.check_param(notname)

        self.assertTrue(template.check_param(name))

    def test_check_param_not_simple_name(self):

        notparam = Name(Uri('x'))
        template = Template(Name('x'), [], [], None)

        with self.assertRaises(UnexpectedType):
            template.check_param(notparam)

        notparam = Name(Self())

        with self.assertRaises(UnexpectedType):
            template.check_param(notparam)

    def test_check_param_too_many_names(self):

        notparam = Name('x', 'y')
        template = Template(Name('x'), [], [], None)

        with self.assertRaises(UnexpectedType):
            template.check_param(notparam)

    def test_as_triples_empty(self):

        template = Template(Name('x'), [], [], None)

        self.assertEqual(template.as_triples(self.env), [])

    def test_as_triples_simple_triple(self):

        template = self.parser.parse('t()(x = z)')[0]
        expect = [(Self(), Name('x').evaluate(self.env), Name('z').evaluate(self.env))]

        self.assertEqual(template.as_triples(self.env), expect)
