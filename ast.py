import string
import collections

zero_argument_fns = []

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

    def get_type(self):
        """Should be overridden in subclasses to return the type of the result."""
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

    def get_type(self, expr1_type, expr2_type):
        if self.value in ('+', '-', '-', '/'):
            return expr1_type  # Raise error if they're not the same?
        elif self.value in ('<', '<=', '==', 'not'):
            return bool
        elif self.value == 'ord':
            return int
        elif self.value == 'chr':
            return chr
        else:
            raise AssertionError

    def make_fn(self, value):
        if value in self.operators:
            return value
        else:
            raise AssertionError

    def _emit(self):
        return self.operators[self.value]
