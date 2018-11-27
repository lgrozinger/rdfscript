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

    def __init__(self, target, path, location):
        super().__init__(location)
        self._target = target
        self._type = 'Import Failure Error'
        self._path = path

    @property
    def target(self):
        return self._target

    def __str__(self):
        return super().__str__() + format("Could not find import '%s'\non path %s\n\n"
                                          % (self.target, self._path))

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
        return super().__str__() + format("Cannot find template '%s'.\n\n" % self.template)

class NoSuchExtension(RDFScriptError):

    def __init__(self, name, location):
        self._name = name
        self._type = 'Extension Not Found Error'

    @property
    def name(self):
        return self._name

    def __str__(self):
        return super().__str__() + format("Cannot find extension '%s'.\n\n" % self.name)

class ExtensionFailure(RDFScriptError):

    def __init__(self, message, location):
        super().__init__(location)
        if message:
            self._message = message
        else:
            self._message = (f"An extension failed, but author did not provide message.")

        self._type = 'Extension Failed Error'

    def __str__(self):
        return super().__str__() + format("%s" % self._message)

class UnknownConstruct(RDFScriptError):

    def __init__(self, construct, location):
        super().__init__(location)
        self._construct = construct

    @property
    def construct(self):
        return self._construct

    def __str__(self):
        return super().__str__() + format("%s cannot be evaluated.\n\n" % self.construct)


