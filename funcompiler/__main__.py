from module import Module
from expression import Int, Identifier, BinaryOperator, Operator, FunctionApplication
from declaration import FunctionDeclaration, Declarations
from ast import Scope

#module = Module(id=Identifier("foo"), expr=Int(42)) # module foo = 42
#module = Module(id=Identifier("bar"), expr=Identifier("x"), decls=Declarations(decls=[FunctionDeclaration(id=Identifier("x"), expr=Int(3))])) # module bar = x where { x = 3 }
#module = Module(id=Identifier("bar"), expr=BinaryOperator(expr1=Identifier("x"), op=Operator("+"), expr2=Int(1)), decls=Declarations(decls=[FunctionDeclaration(id=Identifier("x"), expr=BinaryOperator(expr1=Int(3), op=Operator("*"), expr2=Int(2)))])) # module bar = x + 1 where { x = 3 * 2 }

scope = Scope()

module = Module(id=Identifier("bar"), expr=FunctionApplication(func=Identifier("f"), expr=Int(2)), decls=Declarations(decls=[FunctionDeclaration(scope, id=Identifier("f"), params=[Identifier("x")], expr=BinaryOperator(expr1=Identifier("x"), op=Operator("*"), expr2=Int(3)))])) # module bar = f 2 where { f x = x * 3 }

module.emit(scope)
