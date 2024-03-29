from functools import total_ordering

import funcompiler.expression

@total_ordering
class Type:
    jvm_code = NotImplemented
    wideness = NotImplemented  # Score for how "wide" this type is. Narrow types are preferred when inferring types.

    def __str__(self):
        return self.__class__.__name__

    def __lt__(self, other):
        return self.wideness < other.wideness

    def __eq__(self, other):
        return self.wideness == other.wideness

    @property
    def progression(self):
        return [self]

class GenericType(Type):
    wideness = 10

    def __init__(self, num):
        self._num = num

    def __str__(self):
        return 't' + str(self._num)

class Int(Type):
    jvm_code = 'I'
    wideness = 1

class Double(Type):
    jvm_code = 'D'
    wideness = 5

class Bool(Type):
    jvm_code = 'B'
    wideness = 5

class Char(Type):
    jvm_code = 'C'
    wideness = 5

class Data(Type):
    wideness = 5

    def __init__(self, identifier):
        self._identifier = identifier

    @property
    def identifier(self):
        return self._identifier

class List(Type):
    wideness = 5

    def __init__(self, inner_type):
        self._inner_type = inner_type

    @property
    def inner_type(self):
        return self._inner_type

class _ChangeTrackingDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._modified = False

    def __setitem__(self, key, value):
        if key not in self or self[key] > value:
            super().__setitem__(key, value)
            self._modified = True

    @property
    def modified(self):
        return self._modified

    def reset(self):
        self._modified = False

class Function(Type):
    jvm_code = 'LAbstractFunction;'

    def __init__(self, arg_types, return_type):
        self._progression = [*arg_types, return_type]

    def __str__(self):
        return ' -> '.join(map(str, self._progression))

    def apply(self, typ=None):
        if typ:
            assert isinstance(self._progression[0], GenericType) or isinstance(typ, self._progression[0].__class__)
        
        if len(self._progression) == 2:
            return self._progression[1]
        else:
            return Function(self._progression[1:-1], self._progression[-1])

    @classmethod
    def infer_types(cls, args, expr, scope):
        # To start, we assume that each of the arguments can be of any type.
        types = _ChangeTrackingDict()
        for i, arg in enumerate(args):
            types[arg] = GenericType(i)

        expr.infer_types(types, scope)
        while types.modified:
            types.reset()
            expr.infer_types(types, scope)

        return types

    @property
    def progression(self):
        return self._progression
