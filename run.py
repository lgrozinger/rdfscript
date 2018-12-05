import ply.yacc as yacc
import ply.lex  as lex
import rdflib
import sys
import argparse
import logging

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from rdfscript.SBOL2Serialize import serialize_sboll2

def parse_from_file(filepath,
                    serializer='nt',
                    optpaths=[],
                    out=None,
                    extensions=[]):

    parser = RDFScriptParser(debug=False, filename=filepath)

    with open(filepath, 'r') as in_file:
        data = in_file.read()

    env = Env(filename=filepath,
              serializer=serializer,
              paths=optpaths,
              extensions=extensions)
    forms = parser.parse(data)
    env.interpret(forms)

    if not out:
        print(env)
    else:
        with open(out, 'w') as o:
            o.write(str(env))

def rdf_repl(serializer='nt',
             out=None,
             optpaths=[],
             extensions=[]):
    print("Building parser with yacc...")
    parser = RDFScriptParser()
    print("Parser build success...")
    print("Lexer build success... Enjoy your RDF...")
    print("#"*40)

    env = Env(repl=True,
              serializer=serializer,
              paths=optpaths,
              extensions=extensions)

    while True:
        try:
            if env.default_prefix_set:
                prompt = env.default_prefix.string
            else:
                prompt = 'RDF'

            if sys.version_info >= (3, 0):
                s = input(prompt + '  > ')
            else:
                s = raw_input(prompt + '  > ')
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

def rdfscript_args():

    parser = argparse.ArgumentParser(description="RDFScript interpreter and REPL.")

    parser.add_argument('-s', '--serializer', default='nt',
                        choices=['rdfxml', 'n3', 'turtle', 'sbolxml', 'nt'],
                        help="The format into which the graph is serialised")
    parser.add_argument('-p', '--path',
                        help="Additions to the path in which to search for imports",
                        nargs='*',
                        default=[])
    parser.add_argument('filename', default=None, nargs='?',
                        help="File to parse as RDFScript")

    parser.add_argument('-o', '--output', help="The name of the output file", default=None)
    parser.add_argument('--version', action='version', version='%(prog)s 0.0alpha')
    parser.add_argument('-e', '--extensions', action='append', nargs=2, default=[])

    return  parser.parse_args()

if __name__ == "__main__":

    logging.basicConfig(format='\n%(message)s\n', level=logging.DEBUG)
    args = rdfscript_args()
    extensions = [(ext[0], ext[1]) for ext in args.extensions]

    if args.filename:
        parse_from_file(args.filename,
                        serializer=args.serializer,
                        out=args.output,
                        optpaths=args.path,
                        extensions=extensions)
    else:
        rdf_repl(serializer=args.serializer,
                 out=args.output,
                 optpaths=args.path,
                 extensions=extensions)
