import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex
import rdflib
import pathlib

from rdfscript.env import Env
from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.importer import Importer

class ImporterTest(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def tearDown(self):
        pass

    def test_importer_setup(self):

        i = Importer()

        self.assertEqual(i.path, [pathlib.Path('.').resolve()])

    def test_importer_setup_extras(self):

        p = ['..', '~/']
        i = Importer(extrapaths=p)

        expected = [pathlib.Path('..').resolve(),
                    pathlib.Path('~/').expanduser().resolve(),
                    pathlib.Path('.').resolve()]

        self.assertEqual(i.path, expected)

    def test_importer_add_path(self):

        i = Importer()

        before = [p for p in i.path]
        i.add_path('~/')
        after = i.path

        self.assertEqual(after, before + [pathlib.Path('~/').expanduser().resolve()])

    def test_importer_remove_path(self):

        i = Importer()

        i.remove_path('.')

        self.assertEqual(len(i.path), 0)

    def test_importer_test_files(self):

        env = Env(extrapaths=["test/test_files/"])

        parser = RDFScriptParser()

        with open("test/test_files/top.rdfsh", 'r') as f:
            script = f.read()

        try:
            result = parser.parse(script)
            env.interpret(result)
        except Exception as e:
            self.fail(e)

        self.assertEqual(len(result), 5)
