import ply.lex as leex

tokens = (
    "SYMBOL",
    "BOOLEAN",
    "STRING",
    "INTEGER",
    "DOUBLE",
    "URI",
    "INDENT",
    "DEDENT",
    "RARROW")

t_ignore = ' \t'
literals = ['=', '@', '(', ')', '.', '[', ']', ';', ',', ':']

reserved_words = {
    'true'           : 'BOOLEAN',
    'false'          : 'BOOLEAN',
    }

def t_RARROW(t):
    r'''=>'''
    t.value = '=>'
    return t

def t_STRING(t):
    r'(?:").*?(?:")'
    t.value = t.value[1:-1]
    return t;

def t_DOUBLE(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t;

def t_INTEGER(t):
    r'[-]?\d+'
    t.value = int(t.value)
    return t;

def t_URI(t):
    r'<[^<>]*>'
    t.value = t.value[1:-1]
    return t;

def t_SYMBOL(t):
    r'[^()=:;."\'\s#\[\],]+'
    t.type = reserved_words.get(t.value, 'SYMBOL')
    return t;

def t_COMMENT(t):
    r'\#.*'
    pass;

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value);

def t_error(t):
    print("Could no scan token '%s' at line %d" % (t.value[0], t.lexer.lineno))
    t.lexer.skip(1)




