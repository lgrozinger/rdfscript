import unittest

loader = unittest.TestLoader()

suite = unittest.TestSuite()
suite.addTests(loader.discover('.'))

runner = unittest.TextTestRunner()
result = runner.run(suite)
