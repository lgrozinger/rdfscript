import rdfscript.runtime as runtime
import rdfscript.rdfscriptparser as parser
import rdfscript.evaluate as evaluate

import sys


def code_eval(code_as_string, rt):
    p = parser.RDFScriptParser()

    forms = p.parse(code_as_string)
    for form in forms:
        evaluate.evaluate(form, rt)

    rt.graph_dump()


if __name__ == "__main__":
    rt = runtime.Runtime()
    for line in sys.stdin:
        code_eval(line, rt)
