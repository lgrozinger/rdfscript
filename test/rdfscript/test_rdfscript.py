import unittest

tests = ["test.rdfscript.core.test_context",
         "test.rdfscript.core.test_environment_graph",
         "test.rdfscript.core.test_resolver",
         "test.rdfscript.core.test_creator",
         "test.rdfscript.core.test_core_name",
         "test.rdfscript.core.test_core_prefixes",
         "test.rdfscript.core.test_core_threes",
         "test.rdfscript.core.test_core_twos",
         "test.rdfscript.core.test_core_value",
         "test.rdfscript.core.test_core_uri",
         "test.rdfscript.core.test_utils",
         "test.rdfscript.core.test_runtime",
         "test.rdfscript.core.test_prefix_evaluate",
         "test.rdfscript.core.test_evaluate_using",
         "test.rdfscript.core.test_evaluate_assignment",
         "test.rdfscript.reader.test_reader_bracket",
         "test.rdfscript.reader.test_reader_comments",
         "test.rdfscript.reader.test_reader_doubles",
         "test.rdfscript.reader.test_reader_integers",
         "test.rdfscript.reader.test_reader_pragmas",
         "test.rdfscript.reader.test_reader_reserved_words",
         "test.rdfscript.reader.test_reader_special_tokens",
         "test.rdfscript.reader.test_reader_strings",
         "test.rdfscript.reader.test_reader_symbols",
         "test.rdfscript.reader.test_reader_uri",
         "test.rdfscript.reader.test_reader_whitespace",
         "test.rdfscript.parser.test_parser_assignment",
         "test.rdfscript.parser.test_parser_literals",
         "test.rdfscript.parser.test_parser_triples",
         "test.rdfscript.parser.test_parser_names",
         "test.rdfscript.parser.test_parser_prefixing",
         "test.rdfscript.parser.test_parser_using",
         "test.rdfscript.parser.test_parser_templates",
         "test.rdfscript.parser.test_parser_expansions",
         "test.rdfscript.template.test_template",
         "test.rdfscript.template.test_template_graph",
         "test.rdfscript.template.test_triple_template",
         "test.rdfscript.expansion.test_expansion_graph"]


loader = unittest.TestLoader()
suite = loader.loadTestsFromNames(tests)
runner = unittest.TextTestRunner()
result = runner.run(suite)
