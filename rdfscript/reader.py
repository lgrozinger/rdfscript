import ply.lex as leex

tokens = (
    "SYMBOL",
    "BOOLEAN",
    "STRING",
    "INTEGER",
    "DOUBLE",
    "URI",
    "NEWLINE",
    "INDENT",
    "DEDENT",
    "IMPORT",
    "PREFIX",
    "DEFAULTPREFIX")

t_ignore = '\t'
literals = ['=', '@', '(', ')', '.', '[', ']', ';', ',', ':']

reserved_words = {
    'true'           : 'BOOLEAN',
    'false'          : 'BOOLEAN',
    '@import'        : 'IMPORT',
    '@prefix'        : 'PREFIX',
    '@defaultPrefix' : 'DEFAULTPREFIX'
    }

def t_STRING(t):
    r'(?:").*?(?:")'
    if t.lexer.at_line_start:
        check_for_complete_dedent(t)

    t.value = t.value[1:-1]
    return t;

def t_DOUBLE(t):
    r'\d+\.\d+'
    if t.lexer.at_line_start:
        check_for_complete_dedent(t)

    t.value = float(t.value)
    return t;

def t_INTEGER(t):
    r'[-]?\d+'
    if t.lexer.at_line_start:
        check_for_complete_dedent(t)

    t.value = int(t.value)
    return t;

def t_URI(t):
    r'<[^<>]*>'
    if t.lexer.at_line_start:
        check_for_complete_dedent(t)

    t.value = t.value[1:-1]
    return t;

def t_SYMBOL(t):
    r'[^()=:;."\'\s#\[\],]+'
    t.type = reserved_words.get(t.value, 'SYMBOL')
    if t.lexer.at_line_start:
        check_for_complete_dedent(t)
    return t;

def t_COMMENT(t):
    r'[ ]*\#[^\n]*'
    pass;

def t_newline(t):
    r'[ ]*\n+'
    t.lexer.lineno += len(t.value)
    t.lexer.at_line_start = True

def t_WS(t):
    r'[ ]+'
    if t.lexer.at_line_start:
        space = len(t.value)
        stack = t.lexer.indent_stack
        if space > stack[-1]:
            t.type = 'INDENT'
            stack.append(space)
            t.lexer.at_line_start = False
            return t
        elif space < stack[-1]:
            t.type = 'DEDENT'
            stack.pop()
            t.lexer.lexpos -= space
            return t
        else:
            t.lexer.at_line_start = False
    pass

def t_error(t):
    print("Could no scan token '%s' at line %d" % (t.value[0], t.lexer.lineno))
    t.lexer.skip(1)

def check_for_complete_dedent(t):
    if len(t.lexer.indent_stack) > 1:
        t.type = 'DEDENT'
        t.lexer.indent_stack.pop()
        t.lexer.lexpos -= len(t.value)
        if len(t.lexer.indent_stack) == 1:
            t.lexer.at_line_start = False

    else:
        t.lexer.at_line_start = False
