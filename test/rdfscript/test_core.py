import unittest

import rdflib

from rdfscript.core import (Uri,
                            Value,
                            Name,
                            Prefix,
                            LocalName)

from rdfscript.env import Env

class CoreTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()

    def tearDown(self):
        None

    def test_prefix_init(self):

        self.assertEqual(Prefix('prefix', None).identity, 'prefix')
        self.assertEqual(Prefix(Uri('http://prefix.test/', None), None).identity, Uri('http://prefix.test/', None))

        self.env.bind_prefix(Prefix('p', None), Uri('http://prefix.test/', None))
        self.assertEqual(Prefix(Uri('http://prefix.test/', None), None).uri(self.env), Uri('http://prefix.test/', None))
        self.assertEqual(Prefix('p', None).uri(self.env), Uri('http://prefix.test/', None))

    def test_localname_init(self):

        self.assertEqual(LocalName('name', None).identity, 'name')

        self.assertEqual(LocalName('name', None).uri(self.env), Uri('name', None))

    def test_name(self):

        p = Prefix('p', None)
        self.env.bind_prefix(p, Uri('http://prefix.test/', None))
        name = Name(p, LocalName('name', None), None)

        self.assertEqual(name.uri(self.env), Uri('http://prefix.test/name', None))

        name = Name(Prefix(Uri('http://uriprefix.test/', None), None), LocalName('name', None), None)
        self.assertEqual(name.uri(self.env), Uri('http://uriprefix.test/name', None))

        name = Name(Prefix(Uri('http://uriprefix.test/', None), None), LocalName(Uri('name#name', None), None), None)
        self.assertEqual(name.uri(self.env), Uri('http://uriprefix.test/name#name', None))

        name = Name(Prefix('p', None), LocalName(Uri('name#name', None), None), None)
        self.assertEqual(name.uri(self.env), Uri('http://prefix.test/name#name', None))

    def test_value(self):

        value = Value(12345, None)
        self.assertEqual(value.value, 12345)

    def test_uri_extend(self):

        uri = Uri('http://test.uri/first', None)
        uri.extend(Uri('second', None))
        self.assertEqual(uri, Uri('http://test.uri/first#second', None))

        uri = Uri('http://test.uri/first', None)
        uri.extend(Uri('second', None), delimiter='/')
        self.assertEqual(uri, Uri('http://test.uri/first/second', None))

