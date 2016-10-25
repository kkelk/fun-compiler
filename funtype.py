class Type:
    pass

class Int(Type):
    pass

class Double(Type):
    pass

class Bool(Type):
    pass

class Char(Type):
    pass

class Function(Type):
    def __init__(self, arg_types, return_type):
        self._progression = [*arg_types, return_type]

    def apply(self, typ):
        assert isinstance(typ, self._progression[0])
        
        if len(self._progression) == 2:
            return self._progression[1]
        else:
            return Function(self._progression[1:-1], self._progression[-1])
