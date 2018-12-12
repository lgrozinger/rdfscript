import ply.yacc as yacc
import ply.lex as lex

from . import reader

from .reader import tokens

from .core import (Uri,
                   Name,
                   Value,
                   Self,
                   Prefix,
                   LocalName)

from .pragma import (PrefixPragma,
                     DefaultPrefixPragma,
                     ImportPragma,
                     ExtensionPragma)

from .templating import Assignment
from .template import (Template,
                       Expansion,
                       Property)

from .error import RDFScriptSyntax


## script level
def p_forms(p):
    '''forms : form forms'''
    p[0] = [p[1]] + p[2]

def p_empty_forms(p):
    '''forms : empty'''
    p[0] =[]

def p_form_types(p):
    '''form : assignment
            | pragma
            | template
            | named_expansion
            | expr'''
    p[0] = p[1]

## assignment
def p_assignment(p):
    '''assignment : name '=' expr'''
    p[0] = Assignment(p[1], p[3], location(p))

## pragma
def p_pragma_prefix(p):
    '''pragma : PREFIX SYMBOL expr'''
    l = location(p)
    p[0] = PrefixPragma(Prefix(p[2], l), p[3], l)

def p_defaultprefix_pragma(p):
    '''pragma : DEFAULTPREFIX SYMBOL'''
    l = location(p)
    p[0] = DefaultPrefixPragma(Prefix(p[2], l) , l)

def p_pragma_import(p):
    '''pragma : IMPORT name'''
    p[0] = ImportPragma(p[2], location(p))

def p_extension_no_args(p):
    '''extension : EXTENSION SYMBOL'''
    p[0] = ExtensionPragma(p[2], [], location(p))

def p_extension_args(p):
    '''extension : EXTENSION SYMBOL '(' exprlist ')' '''
    p[0] = ExtensionPragma(p[2], p[4], location(p))

## expansions and templates
def p_template_with_specialisation(p):
    '''template : name '(' exprlist ')' FROM anon_expansion'''
    anon = p[6]
    base = Expansion(p[1], anon.template, anon.args, [], anon.location)
    p[0] = Template(p[1], p[3], anon.body, base, location(p))

def p_base_template(p):
    '''template : name '(' exprlist ')' FROM indentedinstancebody'''

    p[0] = Template(p[1], p[3], p[6], None, location(p))

def p_expansion(p):
    '''expansion : named_expansion
                 | anon_expansion'''
    p[0] = p[1]

def p_named_expansion(p):
    '''named_expansion : name ISA name '(' exprlist ')' indentedinstancebody'''
    p[0] = Expansion(p[1], p[3], p[5], p[7], location(p))

def p_anon_expansion(p):
    '''anon_expansion : name '(' exprlist ')' indentedinstancebody'''
    p[0] = Expansion(None, p[1], p[3], p[5], location(p))


# def p_triple(p):
#     '''triple : name name expr'''
#     p[0] = TripleObject(p[1], p[2], p[3], location(p))

def p_expr(p):
    '''expr : name
            | literal'''
    p[0] = p[1]

def p_indentedinstancebody(p):
    '''indentedinstancebody : '(' instancebody ')' '''
    p[0] = p[2]

def p_empty_indentedinstancebody(p):
    '''indentedinstancebody : empty'''
    p[0] = []

def p_instancebody(p):
    '''instancebody : bodystatements'''
    p[0] = p[1]

## bodies
def p_bodystatements(p):
    '''bodystatements : bodystatement bodystatements'''
    p[0] = [p[1]] + p[2]

def p_empty_bodystatements(p):
    '''bodystatements : empty'''
    p[0] = []

def p_bodystatement(p):
    '''bodystatement : property
                     | named_expansion
                     | extension'''
    p[0] = p[1]

def p_property(p):
    '''property : name '=' expr
                | name '=' expansion'''
    p[0] = Property(p[1], p[3], location(p))

## lists
def p_exprlist(p):
    '''exprlist : emptylist
                | notemptyexprlist'''
    p[0] = p[1]

def p_not_empty_exprlist_1(p):
    '''notemptyexprlist : expr'''
    p[0] = [p[1]]

def p_not_empty_exprlist_n(p):
    '''notemptyexprlist : expr ',' notemptyexprlist'''
    p[0] = [p[1]] + p[3]

def p_empty(p):
    '''empty :'''
    pass

def p_emptylist(p):
    '''emptylist : empty'''
    p[0] = []

## names
def p_dotted_name(p):
    '''name : dotted_list'''
    l = location(p)
    p[0] = Name(*p[1], location=l)

def p_dotted_list_1(p):
    '''dotted_list : identifier'''
    p[0] = [p[1]]

def p_dotted_list_n(p):
    '''dotted_list : identifier '.' dotted_list'''
    p[0] = [p[1]] + p[3]

def p_identifier(p):
    '''identifier : SYMBOL
                  | uri
                  | self'''
    p[0] = p[1]

def p_self(p):
    '''self : SELF'''
    p[0] = Self(location(p))

def p_uri(p):
    '''uri : URI'''
    p[0] = Uri(p[1], location=location(p))

## literal objects
def p_literal(p):
    '''literal : INTEGER
               | STRING
               | DOUBLE'''
    p[0] = Value(p[1], location(p))

def p_literal_boolean(p):
    '''literal : BOOLEAN'''
    if p[1] == 'true':
        p[0] = Value(True, location(p))
    else:
        p[0] = Value(False, location(p))

## SYNTAX ERROR
def p_error(p):
    if not p:
        pass
    else:
        location = Location(Position(p.lineno, p.lexpos), p.lexer.filename)
        raise RDFScriptSyntax(p, location)

def location(p):
    pos = Position(p.lineno(0), p.lexpos(0))
    return Location(pos, p.parser.filename)

class RDFScriptParser:

    def __init__(self, debug=True, scanner=reader, filename=None):

        self.scanner = lex.lex(module=scanner)
        self.scanner.at_line_start = True
        self.scanner.indent_stack  = [0]
        self.scanner.filename = filename

        self.parser = yacc.yacc(debug=debug)
        self.parser.filename = filename

    def parse(self, script):

        return self.parser.parse(script, lexer=self.scanner, tracking=True)

    def reset(self):

        self.scanner.at_line_start = True
        self.scanner.indent_stack  = [0]

class Position:

    def __init__(self, line, col):

        self._line = line
        self._col  = col

    def __repr__(self):
        return format("(%s, %s)" % (self.line, self.col))

    @property
    def line(self):
        return self._line

    @property
    def col(self):
        return self._col

class Location:

    def __init__(self, position, filename=None):

        self._position = position

        if not filename:
            self._filename = "REPL"
        else:
            self._filename = filename

    def __repr__(self):
        return format("%s in '%s'" % (self.position, self.filename))

    @property
    def position(self):
        return self._position

    @property
    def filename(self):
        return self._filename
