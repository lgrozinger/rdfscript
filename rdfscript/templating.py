import rdflib
import pdb

from .core import Node, Name, Uri, Self
from .error import (TemplateNotFound,
                    UnexpectedType)
from .pragma import (ExtensionPragma)

class Assignment(Node):

    def __init__(self, name, value, location):

        super().__init__(location)
        self._name  = name
        self._value = value

    def __eq__(self, other):
        return (isinstance(other, Assignment) and
                self.name == other.name and
                self.value == other.value)

    def __repr__(self):
        return format("ASSIGN: (%s to %s)" %
                      (self.name, self.value))

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value


