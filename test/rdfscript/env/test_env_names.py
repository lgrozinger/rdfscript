import unittest

import rdfscript.env as env


class TestEnvNames(unittest.TestCase):

    def setUp(self):
        self.context = env.Env()

    def tearDown(self):
        pass

    def test_get_namespace(self):

        bnode = self.context._rdf._g.identifier
        expected = self.context._rdf.from_rdf(bnode)
        actually = self.context.namespace

        self.assertEqual(expected, actually)

    def test_namespace_empty_on_init(self):

        expected = []
        actually = self.context._rdf.get(self.context.namespace, None, None)

        self.assertEqual(expected, actually)

    def test_namespaces_includes_namespace_on_init(self):

        expected = [self.context.namespace]
        actually = self.context.namespaces

        self.assertEqual(expected, actually)

    def test_namespaces_includes_namespace_on_init(self):

        expected = [self.context.namespace, Uri('new')]
        actually = self.context.namespaces

        self.context.add_namespace(Uri('new'))
        self.assertEqual(expected, actually)
