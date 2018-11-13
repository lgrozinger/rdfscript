import ply.yacc as yacc
import ply.lex as lex

from . import reader

from .reader import tokens

from .core import (Uri,
                   Name,
                   Value)

from .pragma import (PrefixPragma,
                     DefaultPrefixPragma,
                     ImportPragma)

from .templating import (Assignment,
                         Template,
                         Property,
                         Parameter)

## old ast
from .toplevel import InstanceExp

def p_toplevels(p):
    '''toplevels : toplevel toplevels'''
    p[0] = [p[1]] + p[2]

def p_empty_toplevels(p):
    '''toplevels : empty'''
    p[0] =[]

def p_toplevel_types(p):
    '''toplevel : expr
                | assignment
                | pragma
                | template
                | instanceexp'''
    p[0] = p[1]

def p_template(p):
    '''template : identifier '(' parameterlist ')' RARROW prefixconstructorapp'''
    p[0] = Template(p[1], p[3], p[6], location(p))

def p_template_noargs(p):
    '''template : identifier RARROW prefixconstructorapp'''
    p[0] = Template(p[1], [], p[3], location(p))

def p_instanceexp(p):
    '''instanceexp : identifier ':' prefixconstructorapp'''
    p[0] = InstanceExp(p[1], p[3], location(p))

def p_pragma_prefix(p):
    '''pragma : PREFIX SYMBOL expr'''
    p[0] = PrefixPragma(p[2], p[3], location(p))

def p_defaultprefix_pragma(p):
    '''pragma : DEFAULTPREFIX identifier'''
    p[0] = DefaultPrefixPragma(p[2], location(p))

def p_pragma_import(p):
    '''pragma : IMPORT expr'''
    p[0] = ImportPragma(p[2], location(p))

def p_assignment(p):
    '''assignment : identifier '=' expr'''
    p[0] = Assignment(p[1], p[3], location(p))

# def p_triple(p):
#     '''triple : identifier identifier expr'''
#     p[0] = TripleObject(p[1], p[2], p[3], location(p))


def p_expr(p):
    '''expr : identifier
            | literal'''
    p[0] = p[1]

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

def p_identifier(p):
    '''identifier : qname
                  | localname
                  | uri'''
    p[0] = p[1]

def p_identifierlist(p):
    '''identifierlist : emptylist
                      | notemptyidentifierlist'''
    p[0] = p[1]

def p_not_empty_identifierlist_1(p):
    '''notemptyidentifierlist : identifier'''
    p[0] = [p[1]]

def p_not_empty_identifierlist_n(p):
    '''notemptyidentifierlist : identifier ',' notemptyidentifierlist'''
    p[0] = [p[1]] + p[3]

def p_qname(p):
    '''qname : SYMBOL '.' SYMBOL'''
    p[0] = Name(p[1], p[3], location(p))

def p_literal(p):
    '''literal : INTEGER
               | STRING
               | DOUBLE
               | BOOLEAN'''
    p[0] = Value(p[1], location(p))

def p_localname(p):
    '''localname : SYMBOL'''
    p[0] = Name(None, p[1], location(p))

def p_parameterlist(p):
    '''parameterlist : emptylist
                     | nonemptyparameterlist'''
    p[0] = p[1]

def p_nonemptyparameterlist_1(p):
    '''nonemptyparameterlist : SYMBOL'''
    p[0] = [Parameter(p[1], location(p))]

def p_nonemptyparameterlist_n(p):
    '''nonemptyparameterlist : SYMBOL ',' nonemptyparameterlist'''
    p[0] = [Parameter(p[1], location(p))] + p[3]

def p_uri(p):
    '''uri : URI'''
    p[0] = Uri(p[1], location(p))

def p_prefixconstructorapp(p):
    '''prefixconstructorapp : tpeconstructor indentedinstancebody'''
    p[0] = p[2]

def p_tpeconstructor_args(p):
    '''tpeconstructor : identifier  '(' exprlist ')' '''
    pass

def p_tpeconstructor_noargs(p):
    '''tpeconstructor : identifier'''

def p_tpeconstructorstar(p):
    '''tpeconstructor : empty'''
    pass

def p_indentedinstancebody(p):
    '''indentedinstancebody : INDENT instancebody DEDENT'''
    p[0] = p[2]

def p_empty_indentedinstancebody(p):
    '''indentedinstancebody : empty'''
    p[0] = []

def p_instancebody(p):
    '''instancebody : bodystatements'''
    p[0] = p[1]

def p_bodystatements(p):
    '''bodystatements : bodystatement bodystatements'''
    p[0] = [p[1]] + p[2]

def p_empty_bodystatements(p):
    '''bodystatements : empty'''
    p[0] = []

## 1.0 also has infixassigment here
def p_bodystatement(p):
    '''bodystatement : property
                     | instanceexp'''
    p[0] = p[1]

def p_property(p):
    '''property : identifier '=' expr'''
    p[0] = Property(p[1], p[3], location(p))

# infixassigment breaks the parser, since it causes SR conflict with
# assignment (resolved by default with shift, which is almost always
# the wrong thing to do in ShortBOL's case)

# def p_infixassignment(p):
#     '''infixassigment : identifier '=' infixconstructorapp'''
#     pass

# def p_infixconstructorapp(p):
#     '''infixconstructorapp : expr identifier expr'''

def p_empty(p):
    '''empty :'''
    pass

def p_emptylist(p):
    '''emptylist : empty'''
    p[0] = []

def p_error(p):
    if p == None:
        pass
    else:
        print("Syntax error!: the offending token is '%s' on line %d"
              % (p.value, location(p)))

def location(p):
    pos = Position(p.lineno, p.lexpos)
    return Location(pos, p.parser.filename)

class RDFScriptParser:

    def __init__(self, debug=False, scanner=reader, filename=None):

        self.scanner = lex.lex(module=scanner)
        self.scanner.at_line_start = True
        self.scanner.indent_stack  = [0]

        self.parser = yacc.yacc(debug=debug)
        self.parser.filename = filename

    def parse(self, script):

        return self.parser.parse(script, lexer=self.scanner)

    def reset(self):

        self.scanner.at_line_start = True
        self.scanner.indent_stack  = [0]

class Position:

    def __init__(self, line, col):

        self._line = line
        self._col  = col

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

    @property
    def position(self):
        return self._position

    @property
    def filename(self):
        return self._filename
