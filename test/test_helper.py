from rdfscript.core import (Value,
                   Name,
                   LocalName,
                   Prefix)

from rdfscript.template import (Property)

def name(l, p=None):

    return Name(prefix(p), LocalName(l, None), None)

def prefix(p):

    if p is not None:
        return Prefix(p, None)
    else:
        return p

def property(name, value):

    return Property(name, value, None)
