import string

from ast import ASTNode, Terminal
from childcount import Exactly, GreaterOrEqual
import funtype

class Expr(ASTNode):
    def get_type(self):
        raise NotImplementedError

class Identifier(Expr, Terminal):
    def __init__(self, value):
        assert type(value) is str
        assert set(value) <= set(string.ascii_letters + string.digits + '_')
        assert value[0] in string.ascii_letters

        self._value = value

    def _emit(self, scope):
        return scope.get_identifier(self.value)

        if args:
            return """
            new {name}Function
            invokespecial {name}Function.<init>()V
            """.format(name=self.value)
        else:
            return scope.get_identifier('{}-inline'.format(self.value))

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

class Operator(Terminal):
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

    def get_type(self, expr1_type):
        if self.value in ('+', '*', '-', '/'):
            return expr1_type
        elif self.value in ('<', '<=', '==', 'not'):
            return Type.Bool
        elif self.value == 'ord':
            return Type.Int
        elif self.value == 'chr':
            return Type.Bool
        else:
            raise AssertionError

    def make_fn(self, value):
        if value in self.operators:
            return value
        else:
            raise AssertionError

    def _emit(self, scope):
        return self.operators[self.value]

class UnaryOperator(Expr):
    required_children = {
        'op': (Exactly(1), Operator),
        'expr': (Exactly(1), Expr)
    }

class BinaryOperator(Expr):
    required_children = {
        'expr1': (Exactly(1), Expr),
        'op': (Exactly(1), Operator),
        'expr2': (Exactly(1), Expr)
    }

    def _emit(self, scope):
        return """
        {expr1}
        {expr2}
        {op}
        """.format(expr1=self.expr1.emit(scope), expr2=self.expr2.emit(scope), op=self.op.emit(scope))

    def get_type(self):
        return self.op.get_type(self.expr1.get_type())

class Lists(Expr):
    required_children = {
        'exprs': (GreaterOrEqual(1), Expr)
    }

class Grouping(Expr):
    required_children = {
        'expr': (Exactly(1), Expr)
    }

class funtypepecification(Expr):
    required_children = {
        'expr': (Exactly(1), Expr),
        'type': (Exactly(1), Type)
    }


class Int(Expr, Terminal):
    make_fn = int
    def _emit(self, scope):
        return 'bipush {}'.format(self.value)

    def get_type(self):
        return funtype.Int

class Double(Expr, Terminal):
    make_fn = float

    def get_type(self):
        return funtype.Double

class Char(Expr, Terminal):
    values = tuple(string.printable)

    def get_type(self):
        return funtype.Char

class Constr(Expr):
    required_children = {
        'id': (Exactly(1), Identifier)
    }

class Constrs(ASTNode):
    required_children = {
        'constrs': (GreaterOrEqual(1))
    }

class Bool(Expr, Terminal):
    values = ('True', 'False')

    def get_type(self):
        return funtype.Bool

class FunctionApplication(Expr):
    required_children = {
        'func': (Exactly(1), Expr),
        'expr': (Exactly(1), Expr)
    }

    def _emit(self, scope):
        return """
        {func}
        dup

        getfield AbstractFunction.remaining_params I

        ; Check if there is exactly 1 remaining param, in which case we need the apply that actually returns the result.
        bipush 1
        if_icmpeq applyfinal{label}

        ; Otherwise, we need the intermediate applies that return Functions.
        {expr}
        invokevirtual AbstractFunction.apply(I)LAbstractFunction;
        ; FIXME TEMP WHILE WE SORT OUT TYPES
        pop
        bipush -99
        goto done{label}

        applyfinal{label}:
        {expr}
        invokevirtual AbstractFunction.apply(I)I

        done{label}:

        """.format(func=self.func.emit(scope), expr=self.expr.emit(scope), label=scope.label)
        
    def get_type(self):
        return self.func.get_type().apply(self.expr.get_type())
