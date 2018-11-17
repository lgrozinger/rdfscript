import ply.yacc as yacc
import ply.lex  as lex
import rdflib
import sys

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env

def parse_from_file(filepath):
    print("Building parser with yacc...")
    parser = RDFScriptParser(filename=filepath)
    print("Parser build success...")
    print("Lexer build success... Enjoy your RDF...")
    print("#"*40)

    with open(filepath, 'r') as in_file:
        data = in_file.read()

    env = Env()
    forms = parser.parse(data)
    env.interpret(forms)

    print(env)

def rdf_repl():
    print("Building parser with yacc...")
    parser = RDFScriptParser()
    print("Parser build success...")
    print("Lexer build success... Enjoy your RDF...")
    print("#"*40)

    e = Env(repl=True)

    while True:
        try:
            s = input('RDF > ')
        except EOFError:
            break
        if not s: continue
        forms = parser.parse(s)
        print(e.interpret(forms))

    print(e)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        rdf_repl()
    else:
        parse_from_file(sys.argv[1])
