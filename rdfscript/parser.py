import ply.yacc as parser

from rdfscript.objects import (Literal,
                               QName,
                               NSPrefix,
                               URI,
                               LocalName,
                               Symbol,
                               TripleObject)

from rdfscript.reader import tokens

def p_forms(p):
    '''forms : form forms'''
    p[0] = [p[1]] + p[2]

def p_empty_forms(p):
    '''forms : empty'''
    p[0] =[]

def p_form_types(p):
    '''form : triple
            | expr'''
    p[0] = p[1]

def p_triple(p):
    '''triple : qname qname  expr ';' '''
    p[0] = TripleObject(p[1], p[2], p[3], p.lineno)

def p_expr(p):
    '''expr : qname
            | literal'''
    p[0] = p[1]

def p_expr_qname_ns_and_local(p):
    '''qname : symbol '.' symbol
             | symbol '.' uri
             | uri '.' symbol
             | uri '.' uri '''
    l = p.lineno
    p[0] = QName(NSPrefix(p[1], l) , LocalName(p[3], l), l)

def p_expr_qname_local_only(p):
    '''qname : symbol
             | uri'''
    l = p.lineno
    p[0] = QName('', LocalName(p[1], l), l)

def p_literal(p):
    '''literal : INTEGER
               | STRING
               | DOUBLE
               | BOOLEAN'''
    p[0] = Literal(p[1], p.lineno)

def p_symbol(p):
    '''symbol : SYMBOL'''
    p[0] = Symbol(p[1], p.lineno)

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

