from ast import ASTNode
from childcount import Exactly, GreaterOrEqual
from expression import Expr, Identifier

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

    def get_type(self):
        return self.expr.get_type()
