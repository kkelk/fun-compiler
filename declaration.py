from ast import ASTNode
from childcount import Exactly, GreaterOrEqual
from expression import Identifier, Expr, Constrs, Type

class Declaration(ASTNode):
    pass

class Declarations(ASTNode):
    required_children = {
        'decls': (GreaterOrEqual(0), Declaration)
    }

    def _emit(self, scope):
        return '\n'.join(map(lambda x: x.emit(scope), self.decls))

class FunctionDeclaration(Declaration):
    required_children = {
        'id': (Exactly(1), Identifier),
        'params': (GreaterOrEqual(0), Identifier),
        'expr': (Exactly(1), Expr)
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _emit(self, scope):
        scope.add_identifier(self.id.value, len(self.params))

        if self.params:
            return_str = """
            .class public {name}Function
            .super java/lang/Object

            .field private param_number I

            // TODO maybe also need to track how many params are needed!

            .method public <init>()V
                aload_0
                invokenonvirtual java/lang/Object/<init>()V
                return
            .end method"""

            for param_num in range(len(self.params[:-1])):
                return_str += """
                .field private param_{param_num} I

                .method public set_{param_num}(I)V
                    // Increment the param_number.
                    // We assume that each set_ will only be called once, at the correct times.
                    aload_0
                    getfield {name}Function.param_number I
                    iinc
                    aload_0
                    putfield {name}Function.param_number I

                    aload_0
                    aload_1
                    putfield {name}Function.param_{param_num} I
                    return
                .end method
                    
                .method private apply_{param_num}(I)A
                .limit stack 10
                    // Create a new copy of this Function, and set the value passed on it.
                    new {name}Function
                    invokespecial {name}Function.<init>()V
                    dup
                    aload_1
                    putfield {name}Function.param_{param_num} I
                """

                # Fill in all of the previously set parameters from *this* Function instance.
                for i in range(param_num):
                    return_str += """
                    dup
                    aload_0
                    getfield {name}Function.param_{i} I
                    invokevirtual set_{i}
                    """.format(name=self.id.value, i=i)

                return_str += """
                .end method
                """

            # The final apply is different, as it returns a non-Function result.
            return_str += """
            .method private apply_{param_num}(I)I
            .limit stack 10
                {expr}
                ireturn
            .end method
            """.format(param_num=(len(self.params) - 1), expr=self.expr.emit(scope))
            
            # Top-level apply that dispatches the appropriate apply() based on state.
            # TODO need one of these for each argument type we take.
            return_str += """
            .method public apply_partial(I)A
                aload_0
                getfield {name}Function.param_number
            """

            # Loop through each possible param number and check if its right, then jump
            # to the appropriate dispatch.
            for param_num in range(len(self.params[:1])):
                return_str += """
                dup
                bipush {param_num}
                if_icmpeq apply_{param_num}
                """.format(param_num=param_num)

            # Add all of the dispatches with labels.
            for param_num in range(len(self.params[:1])):
                return_str += """
                apply_{param_num}:
                aload_0
                aload_1
                invokevirtual apply_{param_num}(I)A
                areturn
                """.format(param_num=param_num)

            return_str += """
            .end method
            """

            # Note for self tomorrow: TODO write the method for dispatching the FINAL argument
            # Might just want to do this in the FunctionApplication though.
            # Need to make the param_num public, or a bool whether to dispatch final maybe?
            
            return return_str.format(name=self.id.value)
        else:
            return """
            .method public {name}V
                {expr}
                return
            .end method
            """.format(name=self.id.value, expr=self.expr.emit(scope))

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
