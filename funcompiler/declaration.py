from funcompiler.funast import ASTNode
from funcompiler.childcount import Exactly, GreaterOrEqual
from funcompiler.expression import Identifier, Expr, Constr, Type

from funcompiler.funtype import Function, Data
from funcompiler import util

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

        types = Function.infer_types(self.params, self.expr, scope)
        
        param_types = []
        for param in self.params:
            param_types.append(types[param])

        fun_type = Function(param_types, types[self.expr])

        scope.add_identifier_type(self.id.value, fun_type)
        scope.add_identifier(self.id.value, fun_type, 1)

    def _header(self):
        """Defines the class, its fields and constructor."""
        return_str = """
        .class public {name}Function
        .super AbstractFunction"""

        for param_num in range(len(self.params[:-1])):
            return_str += """
            .field private param_{param_num} Ljava/lang/Object;
            """.format(param_num=param_num)

        return_str += """
        .method public <init>()V
            .limit stack 2
            aload_0
            invokenonvirtual AbstractFunction/<init>()V

            aload_0
            bipush {param_count}
            putfield AbstractFunction.remaining_params I
            return
        .end method"""

        return return_str

    def _tostring(self):
        """Defines the function's toString() method."""
        return_str = """
        .method public toString()Ljava/lang/String;
        .limit locals 2
        .limit stack 4

        {create}
        ldc "{name}Function with bound parameters: "
        {append}
        """.format(name=self.id.value, create=util.create_stringbuilder(), append=util.add_to_stringbuilder())
        
        for param_num in range(len(self.params[:-1])):
            return_str += """
            aload_0
            getfield {name}Function.param_{param_num} Ljava/lang/Object;
            dup
            ifnull skip{param_num}
            
            ldc "("
            {append}
            invokevirtual java/lang/Object.toString()Ljava/lang/String;
            {append}
            ldc ") "
            {append}
            goto after{param_num}

            skip{param_num}:
            pop
            after{param_num}:

            """.format(param_num=param_num, name=self.id.value, append=util.add_to_stringbuilder())

        return_str += """
        aload_1
        invokevirtual java/lang/Object.toString()Ljava/lang/String;
        areturn
        .end method
        """

        return return_str

    def _param_application(self):
        return_str = ""
        for param_num in range(len(self.params[:-1])):
            return_str += """
            .method public set_{param_num}(Ljava/lang/Object;)V
                ; Increment the param_number.
                ; We assume that each set_ will only be called once, at the correct times.
                .limit locals 2
                .limit stack 4
                aload_0
                getfield AbstractFunction.param_number I
                iconst_1
                iadd
                aload_0
                swap
                putfield AbstractFunction.param_number I

                ; And decrement the remaining_params, so we know when we're done.
                aload_0
                getfield AbstractFunction.remaining_params I
                iconst_1
                isub
                aload_0
                swap
                putfield AbstractFunction.remaining_params I

                ; Set the param_[param_num] variable to the argument passed.
                aload_0
                aload_1
                putfield {name}Function.param_{param_num} Ljava/lang/Object;
                return
            .end method
                
            .method private apply_{param_num}(Ljava/lang/Object;)Ljava/lang/Object;
            .limit stack 4
            .limit locals 2
                ; Create a new copy of this Function, and set the value passed on it.
                new {name}Function
                dup
                invokespecial {name}Function.<init>()V
            """.format(name=self.id.value, param_num=param_num)

            # Fill in all of the previously set parameters from *this* Function instance.
            for i in range(param_num):
                return_str += """
                dup
                aload_0
                getfield {name}Function.param_{i} Ljava/lang/Object;
                invokevirtual {name}Function.set_{i}(Ljava/lang/Object;)V
                """.format(name=self.id.value, i=i)

            return_str += """
            dup
            aload_1
            invokevirtual {name}Function.set_{param_num}(Ljava/lang/Object;)V
            areturn
            .end method
            """.format(name=self.id.value, param_num=param_num)

        return return_str

    def _emit(self, scope):
        if self.params:
            scope.add_identifier(self.id.value, """
            new {name}Function
            dup
            invokespecial {name}Function.<init>()V
            """.format(name=self.id.value), 2)

            return_str = self._header()
            return_str += self._tostring()
            return_str += self._param_application()

            # We need to have the parameters "in-scope", so we copy the global scope and add
            # the code to get each of the parameters to it.
            function_scope = deepcopy(scope)

            for i, param in enumerate(self.params[:-1]):
                function_scope.add_identifier_type(param.value, scope.get_identifier_type(self.id.value).progression[i])
                function_scope.add_identifier(param.value, '''
                aload_0
                getfield {name}Function.param_{i} Ljava/lang/Object;
                '''.format(name=self.id.value, i=i), 1)

            function_scope.add_identifier_type(self.params[-1].value, scope.get_identifier_type(self.id.value).progression[-2])
            function_scope.add_identifier(self.params[-1].value, 'aload_1', 1)

            function_scope.get_reset_stack()
            return_str += """
            .method private apply_{param_num}(Ljava/lang/Object;)Ljava/lang/Object;
            .limit locals 2
            .limit stack {stacklimit}
                {expr}
                areturn
            .end method
            """.format(param_num=(len(self.params) - 1), expr=self.expr.emit(function_scope), stacklimit=function_scope.get_reset_stack() + 10)

            # Top-level apply that dispatches the appropriate apply() based on state.
            return_str += """
            .method public apply(Ljava/lang/Object;)Ljava/lang/Object;
                .limit locals 2
                .limit stack 4
                aload_0
                getfield {name}Function.param_number I
            """

            # Loop through each possible param number and check if its right, then jump
            # to the appropriate dispatch.
            for param_num in range(len(self.params)):
                return_str += """
                dup
                bipush {param_num}
                if_icmpeq apply_{param_num}
                """.format(param_num=param_num)

            # Add all of the dispatches with labels.
            for param_num in range(len(self.params)):
                return_str += """
                apply_{param_num}:
                aload_0
                aload_1
                invokevirtual {name}Function.apply_{param_num}(Ljava/lang/Object;)Ljava/lang/Object;
                areturn
                """.format(name=self.id.value, param_num=param_num)

            return_str += """
            .end method
            """

            return return_str.format(name=self.id.value, param_count=len(self.params))
        else:
            expr_scope = deepcopy(scope)
            expr = self.expr.emit(expr_scope)

            scope.add_identifier('{}'.format(self.id.value), expr, expr_scope.get_reset_stack())
            scope.add_identifier_type('{}'.format(self.id.value), self.expr.get_type(expr_scope))
            return ''

    def _emit_target(self):
        if self.params:
            return '{}Function.j'.format(self.id.value)
        else:
            return ''


class DataTypeDeclaration(Declaration):
    required_children = {
        'id': (Exactly(1), Identifier),
        'constrs': (GreaterOrEqual(1), Constr)
    }

    def _emit(self, scope):
        for constr in self.constrs:
            scope.add_identifier(constr.id.value, 'ldc "{}"'.format(constr.id.value), 1)
            scope.set_definite_identifier_type(constr.id.value, Data(self.id.value))

        return ''

class TypeDeclaration(Declaration):
    required_children = {
        'id': (Exactly(1), Identifier),
        'type': (Exactly(1), Type)
    }

    def _emit(self, scope):
        scope.set_definite_identifier_type(self.id.value, self.type.to_funtype())
        return ''
