import rdfscript.reader
import rdfscript.rdfscriptparser as parser
from rdfscript.env import Env

import logging
import sys

class REPL:

    def __init__(self,
                 serializer='nt',
                 out=None,
                 optpaths=[],
                 optextensions=[],
                 debug=None):

        self.env = Env(repl=True,
                       serializer=serializer,
                       paths=optpaths,
                       extensions=optextensions)

        self.reader = parser.make_lexer()
        self.parser = parser.make_parser()

        self.out_file = out

    def start(self):

        try:
            while True:
                self.read()
                self.evaluate()
        except EOFError:
            self.finish()

    def read(self):
        prompt = self.get_prompt_string()

        if sys.version_info >= (3, 0):
            s = input(prompt + '  > ')
        else:
            s = raw_input(prompt + '  > ')
            
        if not s: self.read()
        self.reader.input(s)
        
    def evaluate(self):
        form = self.parser.parse(lexer=self.reader)
        result = self.env.interpret(form)

        self.pprint(result)

    def pprint(self, value):
        string = format("%s" % value)
        print(string)

    def finish(self):

        if not self.out_file:
            self.pprint(self.env)
        else:
            with open(self.out_file, 'w') as out:
                out.write(str(self.env))
        
    def get_prompt_string(self):
        if self.env.prefix is not None:
            prompt = self.env.prefix_for_uri(self.env.prefix)
        else:
            prompt = 'RDF'

        return prompt
                 
