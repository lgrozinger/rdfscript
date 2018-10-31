import ply.yacc as parser

from rdfscript.toplevel import TripleObject, Assignment
from rdfscript.literal import Literal
from rdfscript.identifier import QName, LocalName, URI
from rdfscript.pragma import PrefixPragma
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
                | constructordef'''
    p[0] = p[1]

def p_constructordef(p):
    '''constructordef : identifier '(' identifierlist ')' RARROW prefixconstructorapp'''
    p[0] = ConstructorDef(p[1], p[3], p.lineno)

def p_constructordef_noargs(p):
    '''constructordef : identifier RARROW prefixconstructorapp'''
    p[0] = ConstructorDef(p[1], [], p.lineno)

def p_instanceexp(p):
    '''instanceexp : identifier ':' prefixconstructorapp'''
    pass

def p_pragma_prefix(p):
    '''pragma : PREFIX SYMBOL expr'''
    p[0] = PrefixPragma(p[2], p[3], p.lineno)

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
    '''exprlist : expr exprlist'''
    p[0] = [p[1]] + p[2]

def p_emptyexprlist(p):
    '''exprlist : emptylist'''
    p[0] = p[1]

def p_identifier(p):
    '''identifier : qname
                  | localname
                  | uri'''
    p[0] = p[1]

def p_identifierlist(p):
    '''identifierlist : identifier identifierlist'''
    p[0] = [p[1]] + p[2]

def p_empty_identifierlist(p):
    '''identifierlist : emptylist'''
    p[0] = p[1]

def p_qname(p):
    '''qname : SYMBOL ':' SYMBOL'''
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
    pass

def p_tpeconstructor_args(p):
    '''tpeconstructor : identifier  '(' exprlist ')' '''
    pass

def p_tpeconstructor_noargs(p):
    '''tpeconstructor : identifier'''

def p_tpeconstructorstar(p):
    '''tpeconstructor : '*' '''
    pass

def p_indentedinstancebody(p):
    '''indentedinstancebody : INDENT instancebody DEDENT
                            | empty'''
    pass

def p_instancebody(p):
    '''instancebody : bodystatements'''
    pass

def p_bodystatements(p):
    '''bodystatements : bodystatement bodystatements
                      | empty'''
    pass

def p_bodystatement(p):
    '''bodystatement : infixassigment
                     | assignment
                     | instanceexp'''
    pass

def p_infixassignment(p):
    '''infixassigment : identifier '=' infixconstructorapp'''
    pass

def p_infixconstructorapp(p):
    '''infixconstructorapp : expr identifier expr'''

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

