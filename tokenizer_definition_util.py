import re
from tokenizer import TokenDefinition

def regex(name, expr, **flags):
    compiled = re.compile(expr)
    def processor(string):
        result = compiled.search(string)
        if result:
            return result.span(0)[1]
        return 0
    return TokenDefinition(name, processor, flags)

def word(name, word, **flags):
    length = len(word)
    def processor(string):
        if string.startswith(word):
            return length
        else:
            return 0
    return TokenDefinition(name, processor, flags)

def wordlist(name, words, **flags):
    def processor(string):
        best_length = 0
        for word in words:
            if len(word) > best_length and string.startswith(word):
                best_length = len(word)
        return best_length
    return TokenDefinition(name, processor, flags)


