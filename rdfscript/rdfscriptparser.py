import ply.yacc as yacc
import ply.lex as lex
import logging
from . import reader

from .reader import tokens

import rdfscript.core as core
import rdfscript.pragma as pragma
import rdfscript.template as template

from .error import RDFScriptSyntax


# script level
def p_forms(p):
    '''forms : form forms'''
    p[0] = [p[1]] + p[2]


def p_empty_forms(p):
    '''forms : empty'''
    p[0] = []


def p_form_types(p):
    '''form : assignment
            | extension
            | pragma
            | template
            | three
            | two'''
    p[0] = p[1]


# assignment
def p_assignment(p):
    '''assignment : name '=' expr'''
    p[0] = core.Assignment(p[1], p[3], location(p))


# triple statements
def p_two(p):
    '''two : expr '>' expr'''
    p[0] = core.Two(p[1], p[3], location(p))


def p_three(p):
    '''three : expr '>' expr '>' expr'''
    p[0] = core.Three(p[1], p[3], p[5], location(p))


# pragma
def p_pragma_prefix(p):
    '''pragma : PREFIX SYMBOL '=' name
              | PREFIX SYMBOL '=' uri'''
    loc = location(p)
    p[0] = pragma.PrefixPragma(p[2], p[4], location=loc)


def p_defaultprefix_pragma(p):
    '''pragma : PREFIX SYMBOL'''
    loc = location(p)
    p[0] = pragma.DefaultPrefixPragma(p[2], location=loc)


def p_pragma_import(p):
    '''pragma : USE name'''
    p[0] = pragma.ImportPragma(p[2], location(p))


def p_extension_no_args(p):
    '''extension : EXTENSION SYMBOL'''
    p[0] = pragma.ExtensionPragma(p[2], [], location(p))


def p_extension_args(p):
    '''extension : EXTENSION SYMBOL '(' exprlist ')' '''
    p[0] = pragma.ExtensionPragma(p[2], p[4], location(p))


# expansions and templates
def p_template(p):
    '''template : name '(' exprlist ')' indentedinstancebody'''
    p[0] = template.Template(p[1], p[3], p[5], location=location(p))


def p_expansion(p):
    '''expansion : name '=' name '(' exprlist ')' indentedinstancebody'''
    p[0] = template.Expansion(p[1], p[3], p[5], p[7], location(p))


def p_anon_expansion(p):
    '''anon_expansion : name '(' exprlist ')' indentedinstancebody'''
    p[0] = template.Expansion(None, p[1], p[3], p[5], location(p))

# def p_triple(p):
#     '''triple : name name expr'''
#     p[0] = TripleObject(p[1], p[2], p[3], location(p))


def p_expr(p):
    '''expr : name
            | uri
            | pragma
            | literal
            | expansion'''
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

# bodies


def p_bodystatements(p):
    '''bodystatements : bodystatement bodystatements'''
    p[0] = [p[1]] + p[2]


def p_empty_bodystatements(p):
    '''bodystatements : empty'''
    p[0] = []


def p_bodystatement(p):
    '''bodystatement : property
                     | expansion
                     | anon_expansion
                     | extension'''
    p[0] = p[1]


def p_property(p):
    '''property : name '=' expr'''
#                | name '=' expansion'''
    p[0] = template.Property(p[1], p[3], location=location(p))

# lists


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

# names


def p_dotted_name(p):
    '''name : dotted_name_list'''
    loc = location(p)
    p[0] = core.Name(*p[1], location=loc)


def p_dotted_list_1(p):
    '''dotted_name_list : identifier'''
    p[0] = [p[1]]


def p_dotted_list_n(p):
    '''dotted_name_list : identifier '.' dotted_name_list'''
    p[0] = [p[1]] + p[3]


def p_identifier(p):
    '''identifier : SYMBOL
                  | self'''
    p[0] = p[1]


def p_self(p):
    '''self : SELF'''
    p[0] = core.Self(location(p))


def p_uri(p):
    '''uri : URI'''
    p[0] = core.Uri(p[1], location=location(p))

# literal objects


def p_literal(p):
    '''literal : INTEGER
               | STRING
               | DOUBLE'''
    p[0] = core.Value(p[1], location(p))


def p_literal_boolean(p):
    '''literal : BOOLEAN'''
    if p[1] == 'true':
        p[0] = core.Value(True, location(p))
    else:
        p[0] = core.Value(False, location(p))

# SYNTAX ERROR


def p_error(p):
    if not p:
        pass
    else:
        if p.lexer.filename is not None:
            location = Location(Position(p.lineno, p.lexpos), p.lexer.filename)
        else:
            location = None

        raise RDFScriptSyntax(p.value, location)


def location(p):
    pos = Position(p.lineno(0), p.lexpos(0))
    if p.parser.filename is not None:
        return Location(pos, p.parser.filename)
    else:
        return None


def make_parser(filename=None):
    parser = yacc.yacc()
    parser.filename = filename
    return parser


def make_lexer(filename=None):
    lexer = lex.lex(module=reader)
    lexer.open_brackets = 0
    lexer.filename = filename
    return lexer


class RDFScriptParser:

    def __init__(self, debug_lvl=0, filename=None):

        self.scanner = make_lexer(filename)
        self.debug = debug_lvl != 0
        self.dbg_logger = None
        if debug_lvl == 2:
            self.dbg_logger = logging.getLogger()

        self.parser = make_parser(filename)

    def parse(self, script):

        return self.parser.parse(script,
                                 lexer=self.scanner,
                                 tracking=True,
                                 debug=self.dbg_logger)


class Position:

    def __init__(self, line, col):

        self._line = line
        self._col = col

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
            return None
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
