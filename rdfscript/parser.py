import ply.yacc as parser

from rdfscript.toplevel import (TripleObject,
                                Assignment,
                                ConstructorDef,
                                InstanceExp)

from rdfscript.literal import Literal

from rdfscript.identifier import QName, LocalName, URI

from rdfscript.pragma import (PrefixPragma,
                              ImportPragma,
                              DefaultPrefixPragma)

from rdfscript.reader import tokens

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
                | constructordef
                | instanceexp'''
    p[0] = p[1]

def p_constructordef(p):
    '''constructordef : identifier '(' identifierlist ')' RARROW prefixconstructorapp'''
    p[0] = ConstructorDef(None, p[1], p[3], [], p.lineno)

def p_constructordef_noargs(p):
    '''constructordef : identifier RARROW prefixconstructorapp'''
    p[0] = ConstructorDef(None, p[1], [], [], p.lineno)

def p_instanceexp(p):
    '''instanceexp : identifier ':' prefixconstructorapp'''
    p[0] = InstanceExp(p[1], p[3], p.lineno)

def p_pragma_prefix(p):
    '''pragma : PREFIX SYMBOL expr'''
    p[0] = PrefixPragma(p[2], p[3], p.lineno)

def p_defaultprefix_pragma(p):
    '''pragma : DEFAULTPREFIX identifier'''
    p[0] = DefaultPrefixPragma(p[2], p.lineno)

def p_pragma_import(p):
    '''pragma : IMPORT expr'''
    p[0] = ImportPragma(p[2], p.lineno)

def p_assignment(p):
    '''assignment : identifier '=' expr'''
    p[0] = Assignment(p[1], p[3], p.lineno)

# def p_triple(p):
#     '''triple : identifier identifier expr'''
#     p[0] = TripleObject(p[1], p[2], p[3], p.lineno)


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
    l = p.lineno
    p[0] = QName(p[1], p[3], l)

def p_literal(p):
    '''literal : INTEGER
               | STRING
               | DOUBLE
               | BOOLEAN'''
    p[0] = Literal(p[1], p.lineno)

def p_localname(p):
    '''localname : SYMBOL'''
    l = p.lineno
    p[0] = LocalName(p[1], l)

def p_uri(p):
    '''uri : URI'''
    p[0] = URI(p[1], p.lineno)

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
    '''bodystatement : assignment
                     | instanceexp'''
    p[0] = p[1]

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
              % (p.value, p.lineno))

