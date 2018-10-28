import ply.yacc as yacc
import ply.lex  as lex
import rdflib
import sys

import rdfscript.parser as parser
import rdfscript.reader as reader
import rdfscript.env as env

def parse_from_file(filepath):
    print("Building parser with yacc...")
    parser = yacc.yacc(module=parser)
    print("Parser build success...")
    print("Building lexer with lex...")
    reader = lex.lex(module=reader)
    reader.at_line_start = True
    reader.indent_stack = [0]
    print("Lexer build success... Enjoy your RDF...")
    print("#"*40)

    with open(filepath, 'r') as in_file:
        data = in_file.read()

    env = env.Env()
    forms = parser.parse(data, lexer=reader)
    env.interpret(forms)

    return env.g

def rdf_repl():
    print("Building parser with yacc...")
    p = yacc.yacc(module=parser)
    print("Parser build success...")
    print("Building lexer with lex...")
    r = lex.lex(module=reader)
    r.at_line_start = True
    r.indent_stack = [0]
    print("Lexer build success... Enjoy your RDF...")
    print("#"*40)

    e = env.Env(repl=True)

    while True:
        try:
            s = input('RDF > ')
        except EOFError:
            break
        if not s: continue
        forms = p.parse(s, lexer=r)
        print(e.interpret(forms))

    print(e.g.serialize(format='xml'))

if __name__ == "__main__":
    if len(sys.argv) == 1:
        rdf_repl()
    else:
        parse_from_file(sys.argv[1])
