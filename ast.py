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

    def generate_code(self):
        raise NotImplementedError

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

class Decl(ASTNode):
    pass

class Decls(ASTNode):
    required_children = {
        'decls': (GreaterOrEqual(0), Decl)
    }

    def generate_code(self):
        return '\n'.join(map(lambda x: x.generate_code(), self.decls))

class Type(ASTNode):
    pass

class Identifier(Expr, Terminal):
    def __init__(self, value):
        assert type(value) is str
        assert set(value) <= set(string.ascii_letters + string.digits + '_')
        assert value[0] in string.ascii_letters

        self._value = value

    def generate_code(self):
        return """iload_0"""

class Int(Expr, Terminal):
    make_fn = int
    def generate_code(self):
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
    values = ('+', '*', '-', '/',
              '<', '<=', '==',
              'ord', 'chr', 'not')

class UnaryOperator(Expr):
    required_children = {
        'op': (Exactly(1), Operator),
        'expr': (Exactly(1), Expr)
    }

class BinaryOperator(Expr):
    required_children = {
        'expr1': (Exactly(1), Expr),
        'op': (Exactly(1), Operator)
    }

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
        'decls': (GreaterOrEqual(0), Decls)
    }

    def generate_code(self):
        return '''
        .class public {name}
        .super java/lang/Object

        .method public static module()I
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
        '''.format(name=self.id.value, decls=self.decls.generate_code(), expr=self.expr.generate_code())

class FuncDecl(Decl):
    required_children = {
        'id': (GreaterOrEqual(1), Identifier),
        'expr': (Exactly(1), Expr)
    }

    def generate_code(self):
        return """
        {expr}
        istore_0
        """.format(expr=self.expr.generate_code())

class TaskFarm(Decl):
    required_children = {
        'id': (Exactly(1), Identifier),
        'constrs': (Exactly(1), Constrs)
    }

class TypeDecl(Decl):
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
    module = Module(id=Identifier("bar"), expr=Identifier("x"), decls=Decls(decls=[FuncDecl(id=Identifier("x"), expr=Int(3))])) # module bar = x where { x = 3 }
    print(module.generate_code())
