from module import Module
from expression import Int, Identifier, BinaryOperator
from declaration import FunctionDeclaration

#module = Module(id=Identifier("foo"), expr=Int(42)) # module foo = 42
#module = Module(id=Identifier("bar"), expr=Identifier("x"), decls=Declarations(decls=[FunctionDeclaration(id=Identifier("x"), expr=Int(3))])) # module bar = x where { x = 3 }
module = Module(id=Identifier("bar"), expr=BinaryOperator(expr1=Identifier("x"), op=Operator("+"), expr2=Int(1)), decls=Declarations(decls=[FunctionDeclaration(id=Identifier("x"), expr=BinaryOperator(expr1=Int(3), op=Operator("*"), expr2=Int(2)))])) # module bar = x + 1 where { x = 3 * 2 }
module.emit()
