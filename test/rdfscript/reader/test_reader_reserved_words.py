import unittest
import ply.lex as leex

import rdfscript.reader as reader


class ReaderReservedTest(unittest.TestCase):

    def setUp(self):
        self.reader = leex.lex(module=reader)
        self.reader.at_line_start = True
        self.reader.indent_stack = [0]

    def tearDown(self):
        None
