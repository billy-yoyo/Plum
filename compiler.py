
from token_parser import TokenParser, TokenParserError

class Compiler:
    def __init__(self, stream=None, definitions=None, post_definitions=None):
        self.stream = stream
        self.definitions = definitions or []
        self.post_definitions = post_definitions or []

    def copy(self, stream):
        return Compiler(stream, definitions=self.definitions, post_definitions=self.post_definitions)

    def define(self, defn):
        self.definitions.append(defn)

    def define_post(self, defn):
        self.post_definitions.append(defn)

    def create_parser(self, flags):
        return TokenParser(self, flags)
    
    def _read_without_post(self, flags):
        for defn in self.definitions:
            starting_index = self.stream.index
            node = None
            try:
                node = defn(self.create_parser(flags))
            except TokenParserError:
                # reset index
                pass
            if node:
                return node
            else:
                self.stream.index = starting_index

    def read_without_post(self, flags):
        node = self._read_without_post(flags)
        while node and node.type == "whitebreak":
            node = self._read_without_post(list(flags) + ["whitebreak"])
        return node

    def _read_post(self, flags, value):
        for defn in self.post_definitions:
            starting_index = self.stream.index
            node = None
            try:
                node = defn(self.create_parser(flags), value)
            except TokenParserError:
                pass
            if node:
                return node
            else:
                self.stream.index = starting_index

    def read_post(self, flags, value):
        node = self._read_post(flags, value)
        while node and node.type == "whitebreak":
            node = self._read_post(list(flags) + ["whitebreak"], value)
        return node

    def read(self, flags):
        node = self.read_without_post(flags)
        if not node:
            return None
        count = 0
        post_node = self.read_post(flags, node)
        while post_node is not None:
            count += 1
            node = post_node
            post_node = self.read_post(flags, node)
        return node

    def read_all(self, flags):
        nodes = []
        node = self.read(flags)
        while node is not None:
            nodes.append(node)
            node = self.read(flags)
        return nodes
