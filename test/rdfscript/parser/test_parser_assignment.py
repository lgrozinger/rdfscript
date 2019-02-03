import unittest
import logging

import rdfscript.rdfscriptparser as parser
import rdfscript.core as core
from rdfscript.template import Expansion


class TestParserAssignment(unittest.TestCase):

    def setUp(self):
        self.parser = parser.RDFScriptParser()

    def tearDown(self):
        None

    def test_assignment_name_string(self):
        script = 'Name = "hello"'
        forms = self.parser.parse(script)

        name = core.Name('Name')
        string = core.Value('hello')
        self.assertEqual(forms, [core.Assignment(name, string)])

    def test_assignment_name_integer(self):
        script = 'Name = 12345'
        forms = self.parser.parse(script)

        name = core.Name('Name')
        integer = core.Value(12345)

        self.assertEqual(forms, [core.Assignment(name, integer)])

    def test_assignment_name_boolean(self):
        script = 'Name = true'
        forms = self.parser.parse(script)

        name = core.Name('Name')
        true = core.Value(True)

        self.assertEqual(forms, [core.Assignment(name, true)])

        script = 'Name = false'
        forms = self.parser.parse(script)

        false = core.Value(False)

        self.assertEqual(forms, [core.Assignment(name, false)])

    def test_assignment_name_double(self):
        script = 'Name = 0.12345'
        forms = self.parser.parse(script)

        name = core.Name('Name')
        double = core.Value(0.12345)

        self.assertEqual(forms, [core.Assignment(name, double)])

    def test_assignment_name_uri(self):
        script = 'Name = <http://uri.org/>'
        forms = self.parser.parse(script)

        name = core.Name('Name')
        uri = core.Uri('http://uri.org/')

        self.assertEqual(forms, [core.Assignment(name, uri)])

    def test_assignment_name_name(self):
        script = 'Name = Name'
        forms = self.parser.parse(script)

        name = core.Name('Name')
        self.assertEqual(forms, [core.Assignment(name, name)])


    @unittest.skip("Self on hold for now.")
    def test_assignment_self_name(self):
        script = 'self.v = Name'
        forms = self.parser.parse(script)

        self.assertEqual(forms, [Assignment(core.Name(Self(), 'v'),
                                            core.Name('Name'))])

    def test_assignment_name_expansion(self):

        script = 'expansion = e = t()'
        forms = self.parser.parse(script)

        name = core.Name('expansion')
        self.assertEqual(forms, [core.Assignment(name,
                                                 Expansion(core.Name('e'),
                                                           core.Name('t'),
                                                           [],
                                                           []))])

