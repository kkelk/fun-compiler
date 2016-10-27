from funcompiler.funast import ASTNode
from funcompiler.childcount import Exactly, GreaterOrEqual
from funcompiler.expression import Identifier, Expr, Constrs, Type

from funcompiler.funtype import Function

from copy import deepcopy

class Declaration(ASTNode):
    def __init__(self, scope, *args, **kwargs):
        super().__init__(*args, **kwargs)

class FunctionDeclaration(Declaration):
    required_children = {
        'id': (Exactly(1), Identifier),
        'params': (GreaterOrEqual(0), Identifier),
        'expr': (Exactly(1), Expr)
    }

    def __init__(self, scope, *args, **kwargs):
        super().__init__(scope, *args, **kwargs)

        types = Function.infer_types(self.params, self.expr)
        
        param_types = []
        for param in self.params:
            param_types.append(types[param])

        scope.add_function(self.id, Function(param_types, types[self.expr]))

    def _emit(self, scope):
        if self.params:
            scope.add_identifier(self.id.value, """
            new {name}Function
            dup
            invokespecial {name}Function.<init>()V
            """.format(name=self.id.value))

            return_str = """
            .class public {name}Function
            .super AbstractFunction

            .method public <init>()V
                .limit stack 2
                aload_0
                invokenonvirtual AbstractFunction/<init>()V

                aload_0
                bipush {param_count}
                putfield AbstractFunction.remaining_params I
                return
            .end method"""

            for param_num in range(len(self.params[:-1])):
                return_str += """
                .field private param_{param_num} I

                .method public set_{param_num}(I)V
                    ; Increment the param_number.
                    ; We assume that each set_ will only be called once, at the correct times.
                    aload_0
                    getfield AbstractFunction.param_number I
                    iinc
                    aload_0
                    putfield AbstractFunction.param_number I
                    
                    ; And decrement the remaining_params, so we know when we're done.
                    aload_0
                    getfield AbstractFunction.remaining_params I
                    bipush 1
                    isub
                    putfield AbstractFunction.remaining_params I

                    ; Set the param_[param_num] variable to the argument passed.
                    aload_0
                    iload_1
                    putfield {name}Function.param_{param_num} I
                    return
                .end method
                    
                .method private apply_{param_num}(I)LAbstractFunction;
                .limit stack 10
                    ; Create a new copy of this Function, and set the value passed on it.
                    new {name}Function
                    invokespecial {name}Function.<init>()V
                    dup
                    iload_1
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

            # We need to have the parameters "in-scope", so we copy the global scope and add
            # the code to get each of the parameters to it.
            function_scope = deepcopy(scope)

            for param, i in enumerate(self.params[:1]):
                function_scope.add_identifier(param, '''
                aload_0
                getfield param_{i}
                '''.format(i=i))

            function_scope.add_identifier(self.params[-1].value, 'iload_1')

            return_str += """
            .method private apply_{param_num}(I)I
            .limit locals 2
            .limit stack 10
                {expr}
                ireturn
            .end method
            """.format(param_num=(len(self.params) - 1), expr=self.expr.emit(function_scope))
            
            # Top-level apply that dispatches the appropriate apply() based on state.
            # TODO need one of these for each argument type we take.
            return_str += """
            .method public apply(I)LAbstractFunction;
                .limit locals 2
                .limit stack 10
                aload_0
                getfield {name}Function.param_number I
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
                iload_1
                invokevirtual {name}Function.apply_{param_num}(I)LAbstractFunction;
                areturn
                """.format(name=self.id.value, param_num=param_num)

            return_str += """
            .end method
            """

            # And the final apply method to return the result.
            return_str += """
            .method public apply(I)I
                .limit locals 2
                .limit stack 2
                aload_0
                iload_1
                invokevirtual {name}Function.apply_{final}(I)I
                ireturn
            .end method
            """.format(name=self.id.value, final=len(self.params) - 1)

            return return_str.format(name=self.id.value, param_count=len(self.params))
        else:
            scope.add_identifier('{}'.format(self.id.value), self.expr.emit(scope))
            return ''

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
