import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex
import rdflib

from rdfscript.rdfscriptparser import RDFScriptParser

from rdfscript.env import Env

from rdfscript.core import (Name,
                            Uri,
                            Value)

from rdfscript.evaluate import evaluate

class RuntimeConstructorDefTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    @unittest.skip("Constructor definitions not yet implemented.")
    def test_constructordef_no_args(self):

        script = (f"Template =>\n"
                  f"  a = 1\n"
                  f"  b = 2")

        forms = self.parser.parse(script)

        env = Env()

        return None
