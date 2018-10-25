import unittest
import ply.lex as leex

import rdfscript.reader as reader

class ReaderCommentTest(unittest.TestCase):

    def setUp(self):
        self.reader = leex.lex(module=reader)

    def tearDown(self):
        None

    def test_comments(self):
        self.reader.input('#Symbol 123 4.56 true')
        token = self.reader.token()

        self.assertEqual(token, None)


if __name__ == '__main__':
    unittest.main()
