import ply.yacc as parser

from rdfscript.toplevel import TripleObject, Assignment
from rdfscript.literal import Literal
from rdfscript.identifier import QName, NSPrefix, LocalName, URI
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
                | pragma'''
    p[0] = p[1]

def p_pragma_prefix(p):
    '''pragma : PREFIX identifier expr'''
    p[0] = p[2]

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

def p_qname(p):
    '''qname : localname '.' localname'''
    l = p.lineno
    p[0] = QName(NSPrefix(p[1].localname, l) , p[3].localname, l)

def p_literal(p):
    '''literal : INTEGER
               | STRING
               | DOUBLE
               | BOOLEAN'''
    p[0] = Literal(p[1], p.lineno)

def p_localname(p):
    '''localname : SYMBOL'''
    l = p.lineno
    p[0] = QName(None, LocalName(p[1], l), l)

def p_uri(p):
    '''uri : URI'''
    p[0] = URI(p[1], p.lineno)

def p_empty(p):
    '''empty :'''
    pass

def p_emptylist(p):
    '''emptylist :empty'''
    p[0] = []
    
def p_error(p):
    if p == None:
        pass
    else:
        print("Syntax error!: the offending token is '%s' on line %d"
              % (p.value, p.lineno))

