class RDFScriptError(Exception):

    def __init__(self, location):
        self._location = location
        self._type = 'RDFScriptError'

    @property
    def location(self):
        return self._location

    def __str__(self):
        return format("ERROR: %s\n at %s:\n" % (self._type, self.location))

class FailToImport(RDFScriptError):

    def __init__(self, target, location):
        super().__init__(location)
        self._target = target
        self._type = 'Import Failure Error'

    @property
    def target(self):
        return self._target

    def __str__(self):
        return super().__str__() + format("Could not find import '%s'\n\n"
                                          % self.target)

class RDFScriptSyntax(RDFScriptError):

    def __init__(self, token, location):
        super().__init__(location)
        self._token = token
        self._type = 'Invalid Syntax Error'

    @property
    def token(self):
        return self._token

    def __str__(self):
        return super().__str__() + format("Did not expect to find '%s'\n\n"
                                          % self.token)

class UnexpectedType(RDFScriptError):
    def __init__(self, expected, actual, location):
        super().__init__(location)
        self._expected = expected
        self._actual = actual
        self._type = 'Unexpected Type Error'

    @property
    def expected(self):
        return self._expected

    @property
    def actual(self):
        return self._actual

    def __str__(self):
        return super().__str__() + format("Expected object of type: %s, but found %s\n\n."
                                          % (self.expected, self.actual))

class PrefixError(RDFScriptError):

    def __init__(self, prefix, location):
        super().__init__(location)
        self._prefix = prefix
        self._type = 'Prefix Error'

    @property
    def prefix(self):
        return self._prefix

    def __str__(self):
        return super().__str__() + format("The prefix '%s' is not bound\n\n." % self.prefix)

class TemplateNotFound(RDFScriptError):

    def __init__(self, template, location):
        super().__init__(location)
        self._template = template
        self._type = 'Template Not Found Error'

    @property
    def template(self):
        return self._template

    def __str__(self):
        return super().__str__() + format("Cannnot find template '%s'.\n\n" % self.template)

class UnknownConstruct(RDFScriptError):

    def __init__(self, construct, location):
        super().__init__(location)
        self._construct = construct

    @property
    def construct(self):
        return self._construct

    def __str__(self):
        return super().__str__() + format("%s is not an RDFScript object.\n\n" % self.construct)


