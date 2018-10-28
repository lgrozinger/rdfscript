import ply.yacc as parser

from reader import tokens

def p_toplevels(p):
    '''toplevels : toplevel toplevels'''
    p[0] = [p[1]] + p[2]

def p_empty_toplevels(p):
    '''toplevels : empty'''
    p[0] =[]

def p_toplevel(p):
    '''toplevel : assignment
                | pragma
                | instanceexp
                | constructordef'''
    p[0] = p[1]

def p_assignment(p):
    '''assignment : identifier '=' expr'''
    pass

def p_constructordef(p):
    '''constructordef : identifier arglist0 RARROW prefixconstructorapp'''
    pass

def p_instanceexp(p):
    '''instanceexp : identifier ':' prefixconstructorapp'''
    pass

## TODO: none comma-seperated list here
def p_pragma(p):
    '''pragma : '@' identifier exprlist'''
    pass

def p_prefixconstructorapp(p):
    '''prefixconstructorapp : tpeconstructor indentedinstancebody'''
    pass

def p_tpeconstructor(p):
    '''tpeconstructor : tpeconstructor1
                      | tpeconstructorstar'''
    pass

def p_tpeconstructor1(p):
    '''tpeconstructor1 : identifier valuelist0'''
    pass

def p_tpeconstructorstar(p):
    '''tpeconstructorstar : '*' '''
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


## these lists may not work / cause SR conflicts
def p_valuelist0(p):
    '''valuelist0 : valuelist
                  | empty'''
    pass

def p_valuelist(p):
    '''valuelist : '(' expr exprlist ')' '''
    pass

def p_arglist0(p):
    '''arglist0 : arglist
                | empty'''
    pass

def p_arglist(p):
    '''arglist : '(' identifier identifierlist ')' '''
    pass

def p_identifier(p):
    '''identifier : qname
                  | localname
                  | uri'''
    p[0] = p[1]

def p_identifierlist(p):
    '''identifierlist : ',' identifier identifierlist
                      | empty'''
    pass

def p_expr(p):
    '''expr : identifier
            | literal'''
    p[0] = p[1]

def p_exprlist(p):
    '''exprlist : ',' expr exprlist
                | empty'''

### I think ShortBOL1.0 grammar is ambigous here, since qname is made
### up of NSPrefix and LocalName both of which have the same rule
def p_qname(p):
    '''qname : localname '.' localname'''
    pass


def p_literal(p):
    '''literal : INTEGER
               | STRING
               | DOUBLE
               | BOOLEAN'''
    pass

def p_localname(p):
    '''localname : SYMBOL'''
    pass

def p_uri(p):
    '''uri : URI'''
    pass

def p_empty(p):
    '''empty :'''
    pass

def p_error(p):
    if p == None:
        pass
    else:
        print("Syntax error!: the offending token is '%s' on line %d"
              % (p.value, p.lineno))

p = parser.yacc()
