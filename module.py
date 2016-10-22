from ast import ASTNode, Scope
from childcount import Exactly, GreaterOrEqual
from expression import Expr, Identifier
from declaration import Declarations

class Module(ASTNode):
    required_children = {
        'id': (Exactly(1), Identifier),
        'expr': (Exactly(1), Expr),
        'decls': (GreaterOrEqual(0), Declarations)
    }

    def _emit_target(self):
        return '{}.j'.format(self.id.value)

    def _emit(self, scope):
        return '''
        .class public {name}
        .super java/lang/Object

        .method public static module()I
            .limit stack 10
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
        '''.format(name=self.id.value, decls=self.decls.emit(scope), expr=self.expr.emit(scope))

    def emit(self, scope=Scope()):
        super().emit(scope)
        with open('AbstractFunction.j', 'w') as abstract_fn_file:
            abstract_fn_file.write("""
            .class public abstract AbstractFunction
            .super java/lang/Object
            .field public param_number I
            .field public remaining_params I = 1

            .method public <init>()V
            aload_0
            invokenonvirtual java/lang/Object/<init>()V
            return
            .end method

            .method public abstract apply(I)I
            .end method

            .method public abstract apply(I)LAbstractFunction;
            .end method
            """)

    def get_type(self):
        return self.expr.get_type()
