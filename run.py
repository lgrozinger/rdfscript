import ply.yacc as yacc
import ply.lex  as lex
import rdflib
import sys
import argparse

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from rdfscript.SBOL2Serialize import serialize_sboll2

def parse_from_file(filepath, serializer='turtle', optpaths=[], out=None):
    parser = RDFScriptParser(debug=True, filename=filepath)

    with open(filepath, 'r') as in_file:
        data = in_file.read()

    env = Env(filename=filepath, serializer=serializer, paths=optpaths)
    forms = parser.parse(data)
    env.interpret(forms)

    if not out:
        print(env)
    else:
        with open(out, 'w') as o:
            o.write(str(env))

def rdf_repl(serializer='turtle', out=None, optpaths=[]):
    print("Building parser with yacc...")
    parser = RDFScriptParser()
    print("Parser build success...")
    print("Lexer build success... Enjoy your RDF...")
    print("#"*40)

    env = Env(repl=True, serializer=serializer, paths=optpaths)

    while True:
        try:
            s = input('RDF > ')
        except EOFError:
            break
        if not s: continue
        forms = parser.parse(s)
        print(env.interpret(forms))

    if not out:
        print(env)
    else:
        with open(out, 'w') as o:
            o.write(str(env))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="RDFScript interpreter and REPL.")

    parser.add_argument('-s', '--serializer', default='turtle',
                        choices=['rdfxml', 'n3', 'turtle', 'sbolxml'],
                        help="The format into which the graph is serialised")
    parser.add_argument('-p', '--path',
                        help="Additions to the path in which to search for imports",
                        nargs='*',
                        default=[])
    parser.add_argument('filename', default=None, nargs='?',
                        help="File to parse as RDFScript")

    parser.add_argument('-o', '--output', help="The name of the output file", default=None)

    args = parser.parse_args()

    if args.filename:
        parse_from_file(args.filename,
                        serializer=args.serializer,
                        out=args.output,
                        optpaths=args.path)
    else:
        rdf_repl(serializer=args.serializer,
                 out=args.output,
                 optpaths=args.path)
