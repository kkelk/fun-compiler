from ast import ASTNode
from childcount import Exactly, GreaterOrEqual

class Declaration(ASTNode):
    pass

class Declarations(ASTNode):
    required_children = {
        'decls': (GreaterOrEqual(0), Declaration)
    }

    def _emit(self):
        return '\n'.join(map(lambda x: x.emit(), self.decls))

class FunctionDeclaration(Declaration):
    required_children = {
        'id': (Exactly(1), Identifier),
        'params': (GreaterOrEqual(0), Identifier),
        'expr': (Exactly(1), Expr)
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.params:
            zero_argument_fns.append(self.id.value)

    def _emit(self):
        if self.params:
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
        else:
            return """
            .method public {name}V
                {expr}
                return
            .end method
            """.format(name=self.id.value, expr=self.expr.emit())

    def _emit_target(self):
        if self.params:
            return '{}Function.j'.format(self.id.value)
        else:
            return ''


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
