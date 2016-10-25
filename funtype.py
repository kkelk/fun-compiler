class Type:
    jvm_code = NotImplemented

class Int(Type):
    jvm_code = 'I'

class Double(Type):
    jvm_code = 'D'

class Bool(Type):
    jvm_code = 'B'

class Char(Type):
    jvm_code = 'C'

class Function(Type):
    jvm_code = 'LAbstractFunction;'

    def __init__(self, arg_types, return_type):
        self._progression = [*arg_types, return_type]

    def apply(self, typ):
        assert isinstance(typ, self._progression[0])
        
        if len(self._progression) == 2:
            return self._progression[1]
        else:
            return Function(self._progression[1:-1], self._progression[-1])
