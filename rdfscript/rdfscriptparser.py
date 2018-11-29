import ply.yacc as yacc
import ply.lex as lex

from . import reader

from .reader import tokens

from .core import (Uri,
                   Name,
                   Value,
                   Self)

from .pragma import (PrefixPragma,
                     DefaultPrefixPragma,
                     ImportPragma,
                     ExtensionPragma)

from .templating import (Assignment,
                         Template,
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
    '''assignment : identifier '=' expr'''
    p[0] = Assignment(p[1], p[3], location(p))

## pragma
def p_pragma_prefix(p):
    '''pragma : PREFIX SYMBOL expr'''
    p[0] = PrefixPragma(p[2], p[3], location(p))

def p_defaultprefix_pragma(p):
    '''pragma : DEFAULTPREFIX SYMBOL'''
    p[0] = DefaultPrefixPragma(p[2], location(p))

def p_pragma_import(p):
    '''pragma : IMPORT identifier'''
    p[0] = ImportPragma(p[2], location(p))

def p_extension_no_args(p):
    '''extension : EXTENSION SYMBOL'''
    p[0] = ExtensionPragma(p[2], [], location(p))

def p_extension_args(p):
    '''extension : EXTENSION SYMBOL '(' exprlist ')' '''
    p[0] = ExtensionPragma(p[2], p[4], location(p))

## expansions and templates
def p_template_with_specialisation(p):
    '''template : identifier '(' exprlist ')' RARROW anon_expansion'''
    anon = p[6]
    base = Expansion(anon.template, p[1], anon.args, anon.body, anon.location)
    p[0] = Template(p[1], p[3], [], base, location(p))

def p_base_template(p):
    '''template : identifier '(' exprlist ')' RARROW indentedinstancebody'''

    p[0] = Template(p[1], p[3], p[6], None, location(p))

def p_expansion(p):
    '''expansion : named_expansion
                 | anon_expansion'''
    p[0] = p[1]

def p_named_expansion(p):
    '''named_expansion : identifier ':' identifier '(' exprlist ')' indentedinstancebody'''
    p[0] = Expansion(p[3], p[1], p[5], p[7], location(p))

def p_anon_expansion(p):
    '''anon_expansion : identifier '(' exprlist ')' indentedinstancebody'''
    p[0] = Expansion(p[1], None, p[3], p[5], location(p))


# def p_triple(p):
#     '''triple : identifier identifier expr'''
#     p[0] = TripleObject(p[1], p[2], p[3], location(p))

def p_expr(p):
    '''expr : identifier
            | literal'''
    p[0] = p[1]

def p_indentedinstancebody(p):
    '''indentedinstancebody : INDENT instancebody DEDENT'''
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
    '''property : identifier '=' expr
                | identifier '=' expansion'''
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
def p_identifier(p):
    '''identifier : qname
                  | localname
                  | uri
                  | self'''
    p[0] = p[1]

def p_qname(p):
    '''qname : SYMBOL '.' SYMBOL'''
    p[0] = Name(p[1], p[3], location(p))

def p_localname(p):
    '''localname : SYMBOL'''
    p[0] = Name(None, p[1], location(p))

def p_self(p):
    '''self : SELF'''
    p[0] = Self(location(p))

def p_uri(p):
    '''uri : URI'''
    p[0] = Uri(p[1], location(p))

## literal objects
def p_literal(p):
    '''literal : INTEGER
               | STRING
               | DOUBLE
               | BOOLEAN'''
    p[0] = Value(p[1], location(p))

## SYNTAX ERROR
def p_error(p):
    if p == None:
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
