
class Node:
    def __init__(self, type, **properties):
        self.type = type
        for key, value in properties.items():
            setattr(self, key, value)
    
    def __str__(self):
        parse_value = lambda v: str(v) if not isinstance(v, list) and not isinstance(v, tuple) else f"({', '.join(parse_value(sv) for sv in v)})"
        params = ", ".join(["type"] + [f"{k}={parse_value(v)}" for k, v in self.__dict__.items()])
        return f"Node({params})"