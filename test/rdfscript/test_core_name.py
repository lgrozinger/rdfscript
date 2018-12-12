import unittest

from rdfscript.core import Name, Uri

class CoreNameTest(unittest.TestCase):

    def setUp(self):
        None

    def tearDown(self):
        None

    def test_name_init(self):

        name = Name('first', 'second', 'third')
        self.assertEqual(name.names, ['first', 'second', 'third'])

        name = Name(Uri('http://test.eg'), Uri('#fragment'))
        self.assertEqual(name.names, [Uri('http://test.eg'), Uri('#fragment')])

    def test_name_equal(self):

        name1 = Name('first', 'second', 'third')
        name2 = Name('first', 'second', 'third', location=True)
        self.assertEqual(name1, name2)

        name3 = Name('first', 'second')
        self.assertNotEqual(name1, name3)
