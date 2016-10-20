import string
import collections

class ChildCount():
    def valid(self, value):
        """Should be overriden by subclasses to return a boolean indicating whether the given *value* is a valid number for that instance."""
        raise NotImplementedError

class Exactly(ChildCount):
    def __init__(self, value):
        self.value = value

    def valid(self, value):
        return value == self.value

class GreaterOrEqual(ChildCount):
    def __init__(self, value):
        self.value = value

    def valid(self, value):
        return value >= self.value

class ASTNode():
    # Should be set in sub-classes to
    # a dict of {name: (ChildCount, ASTNode)}
    required_children = NotImplemented

    _value = NotImplemented
    
    def __init__(self, **children):
        assert type(self.required_children) is dict
        self._children = {}

        for name, (len_validator, typ) in self.required_children.items():
            if len_validator.valid(0) and name not in children:
                self._children[name] = None
                continue

            assert name in children

            val = children[name]
            if isinstance(val, collections.Iterable):
                val = tuple(val)
                count = len(val)
                for item in val:
                    assert isinstance(item, typ)
            else:
                count = 1
                assert isinstance(val, typ)

            assert len_validator.valid(count)

            self._children[name] = val
            del children[name]
    
        assert len(children) == 0

    def __getattr__(self, name):
        if name in self._children:
            return self._children[name]
        else:
            raise AttributeError

    def _item_str(self, name, child, level):
        if isinstance(child, ASTNode):
            #return '\t' * level + '{}: {}'.format(name, child.__str__(level + 1))
            return child.__str__(name, level + 1)
        elif type(child) is tuple:
            ret = []
            for i, item in enumerate(child):
                string = self._item_str('{}[{}]'.format(name, i), item, level)
                if string:
                    ret.append(string)
            return ''.join(ret)
        return ''

    def __str__(self, identifier=None, level=0):
        identifier_str = '{}:\t'.format(identifier) if identifier else ''
        value_str = ' (= {})'.format(self._value) if self._value is not NotImplemented else ''

        ret = ('\t' * level) + identifier_str + self.__class__.__name__ + value_str + '\n'

        for name, child in self._children.items():
            ret += self._item_str(name, child, level)

        return ret

    def _emit(self):
        raise NotImplementedError

    def _emit_target(self):
        """By default, emit to a return string. Can be overriden in subclasses to return a (non-empty) string indicating the
        file name to write to. In this case, the empty string will be returned from emit()."""
        return ''

    def emit(self):
        """Emits the result of self._emit() to the self._emit_target()."""
        if self._emit_target():
            with open(self._emit_target(), 'w') as outfile:
                outfile.write(self._emit())
            return ''
        else:
            return self._emit()

class Terminal(ASTNode):
    make_fn = NotImplemented
    _children = {}

    def __init__(self, value):
        assert self.make_fn is not NotImplemented
        self._value = self.make_fn(value)

    @property
    def value(self):
        return self._value

class Expr(ASTNode):
    pass

class Declaration(ASTNode):
    pass

class Declarations(ASTNode):
    required_children = {
        'decls': (GreaterOrEqual(0), Declaration)
    }

    def _emit(self):
        return '\n'.join(map(lambda x: x.emit(), self.decls))

class Type(ASTNode):
    pass

class Identifier(Expr, Terminal):
    def __init__(self, value):
        assert type(value) is str
        assert set(value) <= set(string.ascii_letters + string.digits + '_')
        assert value[0] in string.ascii_letters

        self._value = value

    def _emit(self):
        return """
        new {name}Function
        dup
        invokespecial {name}Function.<init>()V
        invokevirtual {name}Function.apply()I
        """.format(name=self.value)

class Int(Expr, Terminal):
    make_fn = int
    def _emit(self):
        return 'bipush {}'.format(self.value)

class Double(Expr, Terminal):
    make_fn = float

class Char(Expr, Terminal):
    values = tuple(string.printable)

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

class FunctionApplication(Expr):
    required_children = {
        'func': (Exactly(1), Expr),
        'expr': (Exactly(1), Expr)
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

    def make_fn(self, value):
        if value in self.operators:
            return value
        else:
            raise AssertionError

    def _emit(self):
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

    def _emit(self):
        return """
        {expr1}
        {expr2}
        {op}
        """.format(expr1=self.expr1.emit(), expr2=self.expr2.emit(), op=self.op.emit())

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

class Module(ASTNode):
    required_children = {
        'id': (Exactly(1), Identifier),
        'expr': (Exactly(1), Expr),
        'decls': (GreaterOrEqual(0), Declarations)
    }

    def _emit_target(self):
        return '{}.j'.format(self.id.value)

    def _emit(self):
        return '''
        .class public {name}
        .super java/lang/Object

        .method public static module()I
            .limit stack 2
            {decls}
            {expr}
            ireturn
        .end method

        .method public static main([Ljava/lang/String;)V
            .limit stack 2
            getstatic java/lang/System/out Ljava/io/PrintStream;
            invokestatic {name}.module()I
            invokevirtual java/io/PrintStream/println(I)V
            return
        .end method
        '''.format(name=self.id.value, decls=self.decls.emit(), expr=self.expr.emit())

class FunctionDeclaration(Declaration):
    required_children = {
        'id': (Exactly(1), Identifier),
        'params': (GreaterOrEqual(0), Identifier),
        'expr': (Exactly(1), Expr)
    }

    def _emit(self):
        return """
        .class public {name}Function
        .super java/lang/Object

        .method public <init>()V
            aload_0

            invokenonvirtual java/lang/Object/<init>()V
            return
        .end method

        .method public apply()I
        .limit stack 10
            {expr}
            ireturn
        .end method
        """.format(name=self.id.value, expr=self.expr.emit())

    def _emit_target(self):
        return '{}Function.j'.format(self.id.value)


class DataTypeDeclaration(Declaration):
    required_children = {
        'id': (Exactly(1), Identifier),
        'constrs': (Exactly(1), Constrs)
    }

class TypeDeclaration(Declaration):
    required_children = {
        'id': (Exactly(1), Identifier),
        'type': (Exactly(1), Type)
    }

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

if __name__ == '__main__':
    #module = Module(id=Identifier("foo"), expr=Int(42)) # module foo = 42
    #module = Module(id=Identifier("bar"), expr=Identifier("x"), decls=Declarations(decls=[FunctionDeclaration(id=Identifier("x"), expr=Int(3))])) # module bar = x where { x = 3 }
    module = Module(id=Identifier("bar"), expr=BinaryOperator(expr1=Identifier("x"), op=Operator("+"), expr2=Int(1)), decls=Declarations(decls=[FunctionDeclaration(id=Identifier("x"), expr=BinaryOperator(expr1=Int(3), op=Operator("*"), expr2=Int(2)))])) # module bar = x + 1 where { x = 3 * 2 }
    module.emit()
