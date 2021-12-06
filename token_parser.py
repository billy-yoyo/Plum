
class TokenParserError(Exception): pass

class TokenParser:
    def __init__(self, compiler, flags):
        self.compiler = compiler
        self.stream = compiler.stream
        self.flags = flags

    def _run_query(self, query, token):
        if isinstance(query, dict):
            for key, value in query.items():
                if getattr(token, key) != value:
                    return False
        elif isinstance(query, list):
            return any(self._run_query(subquery, token) for subquery in query)
        else:
            raise Exception(f"Unknown query {query}")

        return True

    def next_is(self, query):
        token = self.stream.next()
        if token is None:
            return query is None
        
        if self._run_query(query, token):
            return True
        else:
            self.stream.step_back()

    def step_back(self):
        self.stream.step_back()

    def next_might_be(self, query):
        return self.next_is(query)

    def assert_next_is(self, query):
        if not self.next_is(query):
            raise TokenParserError()

    def last_content(self):
        return self.stream.last().content

    def last_type(self):
        return self.stream.last().type

    def has_flags(self, *flags):
        return all(flag in self.flags for flag in flags)

    def has_no_flags(self, *flags):
        return all(flag not in self.flags for flag in flags)

    def has_flag(self, flag):
        return self.has_flags(flag)

    def has_no_flag(self, flag):
        return self.has_no_flags(flag)

    def assert_flags(self, *flags):
        if not self.has_flags(*flags):
            raise TokenParserError()

    def assert_no_flags(self, *flags):
        if not self.has_no_flags(*flags):
            raise TokenParserError()

    def assert_flag(self, flag):
        self.assert_flags(flag)

    def assert_no_flag(self, flag):
        self.assert_no_flags(flag)
    
    def read(self, *flags):
        result = self.compiler.read(flags)
        if result is None:
            raise TokenParserError()
        return result

    def read_many(self, *flags):
        value = self.compiler.read(flags)
        values = []
        while value is not None:
            values.append(value)
            value = self.compiler.read(flags)
        return values

    def maybe_read(self, *flags):
        try:
            return self.read(*flags)
        except TokenParserError:
            return None
    
    def throw(self):
        raise TokenParserError()

    def assert_true(self, value):
        if not value:
            raise TokenParserError()
