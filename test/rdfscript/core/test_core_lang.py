import unittest

import rdfscript.core as core
import rdfscript.error as err


class TestCoreLang(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_type_assert_incorrect_type_single(self):

        with self.assertRaises(err.UnexpectedType):
            core.type_assert(core.Name(''), core.Uri)

    def test_type_assert_incorrect_type_multiple(self):

        with self.assertRaises(err.UnexpectedType):
            core.type_assert(core.Name(''), core.Uri, core.Self)

    def test_type_assert_correct_type_single(self):

        core.type_assert(core.Uri(''), core.Uri)

    def test_type_assert_correct_type_multiple(self):

        core.type_assert(core.Uri(''), core.Name, core.Uri)

    def test_lang_uri_uri(self):

        expected = core.Uri("https://github.com/lgrozinger/rdfscript/lang/Uri")
        actually = core.lang_uri(expected)

        self.assertEqual(expected, actually)

    def test_lang_uri_name(self):

        expected = core.Uri(
            "https://github.com/lgrozinger/rdfscript/lang/Name")
        actually = core.lang_uri(core.Name(''))

        self.assertEqual(expected, actually)

    def test_lang_uri_value(self):

        expected = core.Uri(
            "https://github.com/lgrozinger/rdfscript/lang/Value")
        actually = core.lang_uri(core.Value(12345))

        self.assertEqual(expected, actually)
