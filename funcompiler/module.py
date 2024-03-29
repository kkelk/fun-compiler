from funcompiler.funast import ASTNode, Scope
from funcompiler.childcount import Exactly, GreaterOrEqual
from funcompiler.expression import Expr, Identifier
from funcompiler.declaration import Declaration
from funcompiler import util
from funcompiler import funtype

from itertools import product

class Module(ASTNode):
    required_children = {
        'id': (Exactly(1), Identifier),
        'expr': (Exactly(1), Expr),
        'decls': (GreaterOrEqual(0), Declaration)
    }

    def _emit_target(self):
        return '{}.j'.format(self.id.value)

    def _emit(self, scope):
        return_str = """
        .class public {name}
        .super java/lang/Object

        .method public static module()Ljava/lang/Object;
            {decls}
            {expr}
            areturn
            .limit stack {stacklimit}
        .end method

        .method public static main([Ljava/lang/String;)V
            getstatic java/lang/System/out Ljava/io/PrintStream;
            invokestatic {name}.module()Ljava/lang/Object;
            invokevirtual java/io/PrintStream/println(Ljava/lang/Object;)V
            .limit stack 2
            return
        .end method
        """

        decls = '\n'.join(map(lambda x: x.emit(scope), self.decls))
        expr = self.expr.emit(scope)

        stacklimit = scope.get_reset_stack()
        
        return return_str.format(name=self.id.value, conversion=util.integer_to_int(), decls=decls, expr=expr, stacklimit=stacklimit)

    def emit(self, scope=Scope()):
        super().emit(scope)

        abstract_fn_decl = """
        .class public abstract AbstractFunction
        .super java/lang/Object
        .field protected param_number I
        .field protected remaining_params I = 1

        .method public <init>()V
            aload_0
            invokenonvirtual java/lang/Object/<init>()V
            return
        .end method
        
        .method public abstract apply(Ljava/lang/Object;)Ljava/lang/Object;
        .end method
        """

        with open('AbstractFunction.j', 'w') as abstract_fn_file:
            abstract_fn_file.write(abstract_fn_decl)

    def get_type(self):
        return self.expr.get_type()
