import string

from funcompiler.funast import ASTNode
from funcompiler.childcount import Exactly, GreaterOrEqual
from funcompiler import funtype
from funcompiler import util

class Expr(ASTNode):
    def get_type(self):
        raise NotImplementedError

    def infer_types(self, types):
        """Modify the *types* dictionary to narrow down the possible types of parameters.
        This default implementation can gain no additional information, so just returns what was given."""
        return types

    def __eq__(self, other):
        return self.__class__ == other.__class__ and set(self._children.values()) == set(other._children.values())

    def __hash__(self):
        return hash((self.__class__, *self._children.values()))

class Terminal(Expr):
    make_fn = NotImplemented
    _children = {}

    def __init__(self, value):
        assert self.make_fn is not NotImplemented
        self._value = self.make_fn(value)

    @property
    def value(self):
        return self._value

    def get_type(self):
        raise NotImplementedError

    def infer_types(self, types):
        types[self] = self.get_type()
        return types

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

class Identifier(Expr):
    _children = {}

    def __init__(self, value):
        assert type(value) is str
        assert set(value) <= set(string.ascii_letters + string.digits + '_')
        assert value[0] in string.ascii_letters

        self._value = value

    def _emit(self, scope):
        return scope.get_identifier(self.value)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    @property
    def value(self):
        return self._value

class Type(ASTNode):
    pass

class NamedType(Type):
    required_children = {
        'id': (Exactly(1), Identifier)
    }

class ListType(Type):
    required_children = {
        'type': (Exactly(1), Type)
    }

class FunctionType(Type):
    required_children = {
        'param_type': (Exactly(1), Type),
        'return_type': (Exactly(1), Type)
    }

class Operator(ASTNode):
    _children = {}

    operators = {
            '+': 'iadd',
            '*': 'imul',
            '-': 'isub',
            '/': 'idiv',
            '<': NotImplemented,
            '<=': NotImplemented,
            '==': NotImplemented,
            'ord': NotImplemented,
            'chr': NotImplemented,
            'not': NotImplemented
    }

    def __init__(self, value):
        if value in self.operators:
            self._value = value
        else:
            raise AssertionError

    @property
    def value(self):
        return self._value

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def get_type(self, expr1_type):
        if self.value in ('+', '*', '-', '/'):
            return expr1_type
        elif self.value in ('<', '<=', '==', 'not'):
            return funtype.Bool()
        elif self.value == 'ord':
            return funtype.Int()
        elif self.value == 'chr':
            return funtype.Bool()
        else:
            raise AssertionError

    def make_fn(self, value):
        if value in self.operators:
            return value
        else:
            raise AssertionError

    def infer_unary(self, expr, types):
        self_mapping = {
            'ord': funtype.Int(),
            'chr': funtype.Char(),
            'not': funtype.Bool()
        }

        expr_mapping = {
            'ord': funtype.Char(),
            'chr': funtype.Int(),
            'not': funtype.Bool()
        }
       
        types[self] = self_mapping[self.value]
        types[expr] = expr_mapping[self.value]
        expr.infer_types(types)

    def infer_binary(self, expr1, expr2, types):
        expr1.infer_types(types)
        expr2.infer_types(types)

        if self.value in ('<', '<=', '=='):
            types[self] = funtype.Bool()
        else:
            types[self] = types[expr1]
            types[self] = types[expr2]

        types[expr1] = types[expr2]
        types[expr2] = types[expr1]

        types[expr1] = funtype.Double()
        types[expr2] = funtype.Double()
            
        return types

    def _emit(self, scope):
        return """
        {toint}
        swap
        {toint}
        swap
        {op}
        {tointeger}
        """.format(toint=util.integer_to_int(), op=self.operators[self.value], tointeger=util.int_to_integer())

class UnaryOperator(Expr):
    required_children = {
        'op': (Exactly(1), Operator),
        'expr': (Exactly(1), Expr)
    }

    def infer_types(self, types):
        self.op.infer_unary(self.expr, types)
        types[self] = types[self.op]

        return types

class BinaryOperator(Expr):
    required_children = {
        'expr1': (Exactly(1), Expr),
        'op': (Exactly(1), Operator),
        'expr2': (Exactly(1), Expr)
    }

    def _emit(self, scope):
        print("here4")
        print(scope._identifiers)
        return """
        {expr1}
        {expr2}
        {op}
        """.format(expr1=self.expr1.emit(scope), expr2=self.expr2.emit(scope), op=self.op.emit(scope))

    def get_type(self):
        return self.op.get_type(self.expr1.get_type())

    def infer_types(self, types):
        self.op.infer_binary(self.expr1, self.expr2, types)
        types[self] = types[self.op]

        return types

class Lists(Expr):
    required_children = {
        'exprs': (GreaterOrEqual(1), Expr)
    }

    def _narrow_types(self, types, typ):
        for expr in exprs:
            if types[expr] < typ:
                raise AssertionError
            elif expr not in types or types[expr] > typ:
                types[expr] = typ

    def infer_types(self, types):
        for expr in exprs:
            if expr in types:
                self._narrow_types(types, types[expr])

        return types

class Grouping(Expr):
    required_children = {
        'expr': (Exactly(1), Expr)
    }

class TypeSpecification(Expr):
    required_children = {
        'expr': (Exactly(1), Expr),
        'type': (Exactly(1), Type)
    }


class Int(Terminal):
    make_fn = int
    def _emit(self, scope):
        return 'ldc {}'.format(self.value) + util.int_to_integer()

    def get_type(self):
        return funtype.Int()

class Double(Terminal):
    make_fn = float

    def get_type(self):
        return funtype.Double()

    def _emit(self, scope):
        return 'ldc2_w {}'.format(self.value) + util.double_to_Double()

class Char(Terminal):
    values = tuple(string.printable)

    def get_type(self):
        return funtype.Char()

class Constr(Expr):
    required_children = {
        'id': (Exactly(1), Identifier)
    }

class Constrs(ASTNode):
    required_children = {
        'constrs': (GreaterOrEqual(1))
    }

class Bool(Terminal):
    values = ('True', 'False')

    def get_type(self):
        return funtype.Bool()

class FunctionApplication(Expr):
    required_children = {
        'func': (Exactly(1), Expr),
        'expr': (Exactly(1), Expr)
    }

    def _emit(self, scope):
        return """
        {func}
        checkcast AbstractFunction
        dup
        {expr}
        invokevirtual AbstractFunction.apply(Ljava/lang/Object;)Ljava/lang/Object;
        """.format(func=self.func.emit(scope), expr=self.expr.emit(scope), expr_type=self.expr.get_type().jvm_code, label=scope.label)
        
    def get_type(self):
        return self.func.get_type().apply(self.expr.get_type())
