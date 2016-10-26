from funast import ASTNode, Scope
from childcount import Exactly, GreaterOrEqual
from expression import Expr, Identifier
from declaration import Declaration

from itertools import product

class Module(ASTNode):
    print(Identifier)
    required_children = {
        'id': (Exactly(1), Identifier),
        'expr': (Exactly(1), Expr),
        'decls': (GreaterOrEqual(0), Declaration)
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
        '''.format(name=self.id.value, decls='\n'.join(map(lambda x: x.emit(scope), self.decls)), expr=self.expr.emit(scope))

    def emit(self, scope=Scope()):
        super().emit(scope)

        abstract_fn_decl = """
        .class public abstract AbstractFunction
        .super java/lang/Object
        .field public param_number I
        .field public remaining_params I = 1

        .method public <init>()V
            aload_0
            invokenonvirtual java/lang/Object/<init>()V
            return
        .end method
        """

        # Generate an apply method in the AbstractFunction for each permutation of argtype/return type.
        for argtype, returntype in product(['I', 'D', 'C', 'LAbstractFunction;'], repeat=2):
            abstract_fn_decl += """
            .method public apply({argtype}){returntype}
                .throws InvalidArgumentException
                .limit locals 3
                .limit stack 2
                new java/lang/IllegalArgumentException
                dup
                invokenonvirtual java/lang/IllegalArgumentException/<init>()V
                athrow
            .end method
            """.format(argtype=argtype, returntype=returntype)

        with open('AbstractFunction.j', 'w') as abstract_fn_file:
            abstract_fn_file.write(abstract_fn_decl)

    def get_type(self):
        return self.expr.get_type()
