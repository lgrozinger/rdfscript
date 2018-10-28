import unittest
import ply.lex as leex

import rdfscript.reader as reader

class ReaderIndentationTest(unittest.TestCase):

    def setUp(self):
        self.reader = leex.lex(module=reader)
        self.reader.indent_stack = [0]
        self.reader.at_line_start = True

    def tearDown(self):
        None

    def test_reader_single_block(self):
        self.reader.input("NoIndent\n Indented\nNoIndent")

        tokens = []

        for token in self.reader:
            tokens.append(token)

        self.assertEqual([x.type for x in tokens], ['SYMBOL',
                                                    'INDENT',
                                                    'SYMBOL',
                                                    'DEDENT',
                                                    'SYMBOL'])

    def test_reader_double_block(self):
        self.reader.input("NoIndent\n Indented\n Indented\nNoIndent")

        tokens = []

        for token in self.reader:
            tokens.append(token)

        self.assertEqual([x.type for x in tokens], ['SYMBOL',
                                                    'INDENT',
                                                    'SYMBOL',
                                                    'SYMBOL',
                                                    'DEDENT',
                                                    'SYMBOL'])

    def test_reader_nested_blocks(self):
        self.reader.input("0\n 1\n 1\n  2\n   3\n  2\n 1\n0")

        tokens = []

        for token in self.reader:
            tokens.append(token)

        self.assertEqual([x.type for x in tokens], ['INTEGER',
                                                    'INDENT',
                                                    'INTEGER',
                                                    'INTEGER',
                                                    'INDENT',
                                                    'INTEGER',
                                                    'INDENT',
                                                    'INTEGER',
                                                    'DEDENT',
                                                    'INTEGER',
                                                    'DEDENT',
                                                    'INTEGER',
                                                    'DEDENT',
                                                    'INTEGER'])

    def test_reader_sharp_dedent(self):
        self.reader.input("0\n  1\n    2\n      3\n0")

        tokens = []

        for token in self.reader:
            tokens.append(token)

        self.assertEqual([x.type for x in tokens], ['INTEGER',
                                                    'INDENT',
                                                    'INTEGER',
                                                    'INDENT',
                                                    'INTEGER',
                                                    'INDENT',
                                                    'INTEGER',
                                                    'DEDENT',
                                                    'DEDENT',
                                                    'DEDENT',
                                                    'INTEGER'])


if __name__ == '__main__':
    unittest.main()
