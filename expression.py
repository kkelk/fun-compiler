from ast import ASTNode, Terminal
from childcount import Exactly, GreaterOrEqual

class Expr(ASTNode):
    pass

class Identifier(Expr, Terminal):
    def __init__(self, value):
        assert type(value) is str
        assert set(value) <= set(string.ascii_letters + string.digits + '_')
        assert value[0] in string.ascii_letters

        self._value = value

    def _emit(self):
        if self.value in zero_argument_fns:
            return """
            invokevirtual {name}
            """.format(name=self.value)  # TODO optimisation (in-lining) possible here
        else:
            return """
            new {name}Function
            dup
            invokespecial {name}Function.<init>()V
            """.format(name=self.value)

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

    def _emit(self):
        return """
        {expr1}
        {expr2}
        {op}
        """.format(expr1=self.expr1.emit(), expr2=self.expr2.emit(), op=self.op.emit())

    def get_type(self):
        return self.op.get_type(self.expr1.get_type(), self.expr2.get_type())

class Lists(Expr):
    required_children = {
        'exprs': (GreaterOrEqual(1), Expr)
    }

class Grouping(Expr):
    required_children = {
        'expr': (Exactly(1), Expr)
    }

class TypeSpecification(Expr):
    required_children = {
        'expr': (Exactly(1), Expr),
        'type': (Exactly(1), Type)
    }


class Int(Expr, Terminal):
    make_fn = int
    def _emit(self):
        return 'bipush {}'.format(self.value)

    def get_type(self):
        return int

class Double(Expr, Terminal):
    make_fn = float

    def get_type(self):
        return float

class Char(Expr, Terminal):
    values = tuple(string.printable)

    def get_type(self):
        return chr

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
        return bool

class FunctionApplication(Expr):
    required_children = {
        'func': (Exactly(1), Expr),
        'expr': (Exactly(1), Expr)
    }

    def _emit(self):
        return """
        {func}
        {expr}
        invokevirtual {name}Function.apply()I
        """.format(func=self.func.emit(), expr=self.expr.emit())

