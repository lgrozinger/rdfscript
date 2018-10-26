import ply.yacc as parser

from rdfscript.objects import TripleObject
from rdfscript.literal import Literal
from rdfscript.identifier import QName, NSPrefix, LocalName, URI
from rdfscript.reader import tokens

def p_forms(p):
    '''forms : form forms'''
    p[0] = [p[1]] + p[2]

def p_empty_forms(p):
    '''forms : empty'''
    p[0] =[]

def p_form_types(p):
    '''form : expr
            | triple'''
    p[0] = p[1]

def p_triple(p):
    '''triple : qname qname expr'''
    p[0] = TripleObject(p[1], p[2], p[3], p.lineno)

def p_expr(p):
    '''expr : qname
            | literal'''
    p[0] = p[1]

def p_expr_qname_ns_and_local(p):
    '''qname : localname '.' localname
             | localname '.' uri
             | uri '.' localname'''
    l = p.lineno
    p[0] = QName(NSPrefix(p[1], l) , p[3], l)

def p_expr_qname_bare_uri(p):
    '''qname : uri'''
    p[0] = p[1]

def p_expr_qname_local_only(p):
    '''qname : localname'''
    p[0] = QName(None, p[1], p.lineno)

def p_literal(p):
    '''literal : INTEGER
               | STRING
               | DOUBLE
               | BOOLEAN'''
    p[0] = Literal(p[1], p.lineno)

def p_symbol(p):
    '''localname : SYMBOL'''
    p[0] = LocalName(p[1], p.lineno)

def p_uri(p):
    '''uri : URI'''
    p[0] = URI(p[1], p.lineno)

def p_empty(p):
    '''empty :'''
    pass

def p_error(p):
    if p == None:
        pass
    else:
        print("Syntax error!: the offending token is '%s' on line %d"
              % (p.value, p.lineno))

