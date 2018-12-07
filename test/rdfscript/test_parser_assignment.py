import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex
import logging

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.core import Value, Uri
from rdfscript.templating import Assignment

import test.test_helper as test

class ParserTopLevelTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()
        self.maxDiff = None
        self.logger = logging.getLogger(__name__)

    def tearDown(self):
        None

    def test_assignment_name_string(self):
        script = 'Name = "hello"'
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [Assignment(test.name('Name'),
                                            Value("hello", None),
                                            None)])

    def test_assignment_name_integer(self):
        script = 'Name = 12345'
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [Assignment(test.name('Name'),
                                            Value(12345, None),
                                            None)])

    def test_assignment_name_boolean(self):
        script = 'Name = true'
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [Assignment(test.name('Name'),
                                            Value(True, None),
                                            None)])

        script = 'Name = false'
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [Assignment(test.name('Name'),
                                            Value(False, None),
                                            None)])

    def test_assignment_name_double(self):
        script = 'Name = 0.12345'
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [Assignment(test.name('Name'),
                                            Value(0.12345, None),
                                            None)])

    def test_assignment_name_uri(self):
        script = 'Name = <http://uri.org/>'
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [Assignment(test.name('Name'),
                                            Uri('http://uri.org/', None),
                                            None)])

    def test_assignment_name_name(self):
        script = 'Name = Name'
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [Assignment(test.name('Name'),
                                            test.name('Name'),
                                            None)])

    def test_assignment_uri_string(self):
        script = '<http://uri.org/> = "hello"'
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [Assignment(Uri('http://uri.org/', None),
                                            Value("hello", None),
                                            None)])

    def test_assignment_uri_integer(self):
        script = '<http://uri.org/> = 12345'
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [Assignment(Uri('http://uri.org/', None),
                                            Value(12345, None),
                                            None)])

    def test_assignment_uri_boolean(self):
        script = '<http://uri.org/> = true'
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [Assignment(Uri('http://uri.org/', None),
                                            Value(True, None),
                                            None)])

        script = '<http://uri.org/> = false'
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [Assignment(Uri('http://uri.org/', None),
                                            Value(False, None),
                                            None)])

    def test_assignment_uri_double(self):
        script = '<http://uri.org/> = 0.12345'
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [Assignment(Uri('http://uri.org/', None),
                                            Value(0.12345, None),
                                            None)])

    def test_assignment_uri_uri(self):
        script = '<http://uri.org/> = <http://value.org>'
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [Assignment(Uri('http://uri.org/', None),
                                            Uri('http://value.org', None),
                                            None)])

    def test_assignment_uri_name(self):
        script = '<http://uri.org/> = Name'
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [Assignment(Uri('http://uri.org/', None),
                                            test.name('Name'),
                                            None)])
