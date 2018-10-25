import ply.yacc as parser

import rdfscript.objects

from rdfscript.reader import tokens

def p_forms(p):
    '''forms : form forms'''
    p[0] = [p[1]] + p[2]

def p_empty_forms(p):
    '''forms : empty'''
    p[0] =[]

def p_form_types(p):
    '''form : triple
            | literal'''
    p[0] = p[1]

def p_triple(p):
    '''triple : qname qname expr ';' '''
    p[0] = TripleObject(p[1], p[2], p[3], p.lineno)

def p_expr(p):
    '''expr : qname
            | literal'''
    p[0] = p[1]

def p_expr_qname_ns_and_local(p):
    '''qname : nsprefix '.' localname'''
    p[0] = QName(p[1], p[3], p.lineno)

def p_expr_qname_local_only(p):
    '''qname : localname'''
    p[0] = QName('', p[1], p.lineno)

def p_nsprefix(p):
    '''nsprefix : SYMBOL
                | URI'''
    p[0] = NSPrefix(p[1], p.lineno)

def p_localname(p):
    '''localname : SYMBOL
                 | URI'''
    p[0] = LocalName(p[1], p.lineno)

def p_literal(p):
    '''literal : INTEGER
               | STRING
               | DOUBLE
               | BOOLEAN'''
    p[0] = Literal(p[1], p.lineno)

def p_error(p):
    if p == None:
        pass
    else:
        print("Syntax error!: the offending token is '%s'" % p.value)
