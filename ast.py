import string
import collections

class Scope():
    def __init__(self):
        self._identifiers = {}
        self._label = 0
        self._function_types = {}

    def get_identifier(self, identifier):
        return self._identifiers[identifier]

    def add_identifier(self, identifier, value):
        self._identifiers[identifier] = value

    def add_function(self, fn_id, fn_type):
        self._function_types[fn_id] = fn_type

    def get_function_type(self, fn_id):
        return self._function_types[fn_id]

    @property
    def label(self):
        self._label += 1
        return self._label

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
                self._children[name] = []
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

    def _emit(self, scope):
        raise NotImplementedError

    def get_type(self):
        """Should be overridden in subclasses to return the type of the result."""
        raise NotImplementedError

    def _emit_target(self):
        """By default, emit to a return string. Can be overriden in subclasses to return a (non-empty) string indicating the
        file name to write to. In this case, the empty string will be returned from emit()."""
        return ''

    def emit(self, scope):
        """Emits the result of self._emit() to the self._emit_target()."""
        emit_string = '\n'.join([line.strip() for line in self._emit(scope).split('\n') if line.strip()])

        if self._emit_target():
            with open(self._emit_target(), 'w') as outfile:
                outfile.write(emit_string)
            return ''
        else:
            return emit_string

class Terminal(ASTNode):
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
