
class Token:
    def __init__(self, type, content, flags):
        self.type = type
        self.content = content
        self.flags = flags

class TokenDefinition:
    def __init__(self, name, processor, flags=None):
        self.name = name
        self.processor = processor
        self.flags = flags or {}

class Tokenizer:
    def __init__(self):
        self.definitions = []

    def define(self, defn):
        self.definitions.append(defn)

    def read(self, string):
        best_length, best_defn = 0, None
        for defn in self.definitions:
            length = defn.processor(string)
            if length > best_length:
                best_length, best_defn = length, defn
        
        if best_defn is None:
            return None, string
        else:
            return Token(best_defn.name, string[:best_length], best_defn.flags.copy()), string[best_length:]


class TokenStream:
    def __init__(self, tokenizer, string, tokens=None, index=0):
        self.tokenizer = tokenizer
        self.string = string
        self.tokens = tokens if tokens is not None else []
        self.index = index or 0

    def copy(self):
        return TokenStream(self.tokenizer, self.string, self.tokens, self.index)

    def merge(self, stream):
        self.index = stream.index

    def read(self, index):
        while len(self.tokens) <= index:
            token, string = self.tokenizer.read(self.string)
            if token is None:
                return None
            
            if not token.flags.get("throwaway", False):
                self.tokens.append(token)
            self.string = string
        return self.tokens[index]

    def next(self):
        token = self.read(self.index)
        if token:
            self.index += 1
        return token

    def last(self):
        if self.index > 0:
            return self.read(self.index - 1)

    def step_back(self):
        if self.index > 0:
            self.index -= 1
        return self