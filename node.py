
class Node:
    def __init__(self, type, **properties):
        self.type = type
        for key, value in properties.items():
            setattr(self, key, value)
    