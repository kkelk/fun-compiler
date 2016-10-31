import string

from funcompiler.funast import ASTNode
from funcompiler.childcount import Exactly, GreaterOrEqual
from funcompiler import funtype
from funcompiler import util

class Expr(ASTNode):
    def get_type(self, scope):
        raise NotImplementedError

    def infer_types(self, types, scope):
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

    def get_type(self, scope):
        raise NotImplementedError

    def infer_types(self, types, scope):
        types[self] = self.get_type(scope)
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
        return scope.get_allocate_identifier(self.value)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    @property
    def value(self):
        return self._value

    def get_type(self, scope):
        return scope.get_identifier_type(self.value)

class Type(ASTNode):
    def to_funtype(self):
        raise NotImplementedError

    @property
    def value(self):
        return self._value

class NamedType(Type):
    required_children = {
        'id': (Exactly(1), Identifier)
    }

    named_types = {
            'Int': funtype.Int,
            'Double': funtype.Double,
            'Char': funtype.Char
    }

    def to_funtype(self):
        return self.named_types[self.id.value]

    @property
    def value(self):
        return self._value

class ListType(Type):
    required_children = {
        'type': (Exactly(1), Type)
    }

class FunctionType(Type):
    required_children = {
        'param_type': (Exactly(1), Type),
        'return_type': (Exactly(1), Type)
    }

    def to_funtype(self):
        return funtype.Function([self.param_type.to_funtype()], [self.return_type.to_funtype()])

class Operator(ASTNode):
    _children = {}

    # Mapping from operators to (integer, double) bytecode versions
    boolean_operators = {
            '<': {
                    funtype.Int: '''
                    invokevirtual java/lang/Integer.compareTo(Ljava/lang/Integer;)I
                    iflt true_return
                    goto false_return''',
                    funtype.Double: '''
                    invokevirtual java/lang/Double.compareTo(Ljava/lang/Double;)I
                    iflt true_return
                    goto false_return
                    '''
                },
            '<=': {
                   funtype.Int: '''
                   invokevirtual java/lang/Integer.compareTo(Ljava/lang/Integer;)I
                   ifle true_return
                   goto false_return
                   ''',
                   funtype.Double: '''
                   invokevirtual java/lang/Double.compareTo(Ljava/lang/Double;)I
                   ifle true_return
                   goto false_return
                   '''
                   },
            '==': {funtype.Int: '''
                   invokevirtual java/lang/Integer.compareTo(Ljava/lang/Integer;)I
                   ifeq true_return
                   goto false_return
                   ''',
                   funtype.Double: '''
                   invokevirtual java/lang/Double.compareTo(Ljava/lang/Double;)I
                   ifeq true_return
                   goto false_return
                   ''',
                   funtype.Data: '''
                   invokevirtual java/lang/Object.equals(Ljava/lang/Object;)Z
                   ifeq false_return
                   goto true_return
                   '''
                   },
            'not': {funtype.Bool: '''
                   invokevirtual java/lang/Boolean.booleanValue()Z
                   ifeq true_return
                   goto false_return
                   '''
                   }
    }

    numeric_operators = {
            '+': {
                funtype.Int: 'iadd',
                funtype.Double: 'dadd'
            },
            '*': {
                funtype.Int: 'imul', 
                funtype.Double: 'dmul'
            },
            '-': {
                funtype.Int: 'isub',
                funtype.Double: 'dsub'
            },
            '/': {
                funtype.Int: 'idiv',
                funtype.Double: 'ddiv'
            },
            'chr': {
                funtype.Int: 'i2c' + util.char_to_Character(),
                funtype.Double: 'd2i\ni2c' + util.char_to_Character()
            },
            'ord': {
                funtype.Char: util.int_to_integer()
            }
    }

    operators = {**boolean_operators, **numeric_operators}

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
        if self.value in self.numeric_operators:
            return expr1_type
        elif self.value in self.boolean_operators:
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

    def infer_unary(self, expr, types, scope):
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
        expr.infer_types(types, scope)

    def infer_binary(self, expr1, expr2, types, scope):
        expr1.infer_types(types, scope)
        expr2.infer_types(types, scope)

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

    def emit(self, expr_type, binary, scope):
        op = self.operators[self.value][type(expr_type)]

        if self.value in self.numeric_operators:
            if binary:
                if isinstance(expr_type, funtype.Int):
                    return """
                    {toint}
                    swap
                    {toint}
                    swap
                    {op}
                    {tointeger}
                    """.format(toint=util.integer_to_int(), op=op, tointeger=util.int_to_integer())
                else:
                    scope.allocate_stack(2)
                    return """
                    {todouble}
                    dup2_x1
                    pop2
                    {todouble}
                    dup2_x2
                    pop2
                    {op}
                    {toDouble}
                    """.format(todouble=util.Double_to_double(), op=op, toDouble=util.double_to_Double())
            else:
                conversion = {
                    funtype.Char: util.Character_to_char(),
                    funtype.Int: util.integer_to_int(),
                    funtype.Double: util.Double_to_double()
                }
                return conversion[type(expr_type)] + op
        else:
            return """
            {comparison}
            true_return:
            iconst_1
            goto done
            
            false_return:
            iconst_0
            goto done

            done:
            invokestatic java/lang/Boolean.valueOf(Z)Ljava/lang/Boolean;
            """.format(comparison=op)

class UnaryOperator(Expr):
    required_children = {
        'op': (Exactly(1), Operator),
        'expr': (Exactly(1), Expr)
    }

    def infer_types(self, types, scope):
        self.op.infer_unary(self.expr, types)
        types[self] = types[self.op]

        return types

    def _emit(self, scope):
        return """
        {expr}
        {op}
        """.format(expr=self.expr.emit(scope), op=self.op.emit(self.expr.get_type(scope), False, scope))

    def get_type(self, scope):
        return self.op.get_type(self.expr.get_type(scope))

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
        """.format(expr1=self.expr1.emit(scope), expr2=self.expr2.emit(scope), op=self.op.emit(self.expr1.get_type(scope), True, scope))

    def get_type(self, scope):
        return self.op.get_type(self.expr1.get_type(scope))

    def infer_types(self, types, scope):
        self.op.infer_binary(self.expr1, self.expr2, types, scope)
        types[self] = types[self.op]

        return types

class Lists(Expr):
    required_children = {
        'exprs': (GreaterOrEqual(1), Expr)
    }

    def get_type(self, scope):
        return funtype.List(self.exprs[0].get_type(scope))

    def _narrow_types(self, types, typ):
        for expr in exprs:
            if types[expr] < typ:
                raise AssertionError
            elif expr not in types or types[expr] > typ:
                types[expr] = typ

    def infer_types(self, types, scope):
        for expr in exprs:
            if expr in types:
                self._narrow_types(types, types[expr])

        return types

    def _emit(self, scope):
        scope.allocate_stack(4)
        return_str = """
        new java/util/LinkedList
        dup
        invokenonvirtual java/util/LinkedList/<init>()V
        """

        for expr in self.exprs:
            return_str += """
            dup
            {expr}
            invokevirtual java/util/LinkedList.add(Ljava/lang/Object;)Z
            pop
            """.format(expr=expr.emit(scope))

        return return_str


class Grouping(Expr):
    required_children = {
        'expr': (Exactly(1), Expr)
    }

class TypeSpecification(Expr):
    required_children = {
        'expr': (Exactly(1), Expr),
        'type': (Exactly(1), Type)
    }

    def _emit(self, scope):
        return self.expr.emit(scope)

    def get_type(self):
        return self.type.to_funtype()


class Int(Terminal):
    make_fn = int
    def _emit(self, scope):
        scope.allocate_stack(1)
        return 'ldc {}'.format(self.value) + util.int_to_integer()

    def get_type(self, scope):
        return funtype.Int()

class Double(Terminal):
    make_fn = float

    def get_type(self, scope):
        return funtype.Double()

    def _emit(self, scope):
        scope.allocate_stack(2)
        return 'ldc2_w {}'.format(self.value) + util.double_to_Double()

class Char(Terminal):
    make_fn = lambda self, x: x
    values = tuple(string.printable)

    def get_type(self, scope):
        return funtype.Char()

    def _emit(self, scope):
        scope.allocate_stack(1)
        return 'bipush {}'.format(ord(self.value)) + util.char_to_Character()

class Constr(Expr):
    required_children = {
        'id': (Exactly(1), Identifier)
    }

    def _emit(self, scope):
        scope.allocate_stack(1)
        return scope.get_identifier(self.id.value)

    def get_type(self, scope):
        return scope.get_identifier_type(self.id.value)

class Bool(Terminal):
    values = ('True', 'False')
    make_fn = lambda self, x: x

    def get_type(self, scope):
        return funtype.Bool()

    def _emit(self, scope):
        scope.allocate_stack(1)
        val = 1 if self.value == 'True' else 0
        return '''
        iconst_{val}
        invokestatic java/lang/Boolean.valueOf(Z)Ljava/lang/Boolean;
        '''.format(val=val)

class FunctionApplication(Expr):
    required_children = {
        'func': (Exactly(1), Expr),
        'expr': (Exactly(1), Expr)
    }

    def _emit(self, scope):
        scope.allocate_stack(1)
        return """
        {func}
        checkcast AbstractFunction
        dup
        {expr}
        invokevirtual AbstractFunction.apply(Ljava/lang/Object;)Ljava/lang/Object;
        """.format(func=self.func.emit(scope), expr=self.expr.emit(scope))
        
    def get_type(self, scope):
        return self.func.get_type(scope).apply(self.expr.get_type(scope))
