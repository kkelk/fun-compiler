from funcompiler.ast import Scope
from funcompiler.module import Module
from funcompiler.expression import *
from funcompiler.declaration import *

import subprocess

def run(module_name):
    make_process = subprocess.run('java -jar jasmin.jar *.j', shell=True, check=True)
    return subprocess.check_output(['java', module_name])

def check(module, expected_output, scope=None):
    if not scope:
        scope = Scope()

    module.emit(scope)
    assert run(module.id) == expected_output

def test_int():
    module = Module(id=Identifier("foo"), expr=Int(42)) # module foo = 42
    check(module, 42)

def test_zero_args():
    scope = Scope()

    module = Module(id=Identifier("bar"), expr=Identifier("x"), decls=Declarations(decls=[FunctionDeclaration(scope, id=Identifier("x"), expr=Int(3))])) # module bar = x where { x = 3 }
    check(module, 3)

def test_operators():
    scope = Scope()

    module = Module(id=Identifier("bar"), expr=BinaryOperator(expr1=Identifier("x"), op=Operator("+"), expr2=Int(1)), decls=Declarations(decls=[FunctionDeclaration(scope, id=Identifier("x"), expr=BinaryOperator(expr1=Int(3), op=Operator("*"), expr2=Int(2)))])) # module bar = x + 1 where { x = 3 * 2 }
    check(module, 7, scope)

def test_one_arg():
    scope = Scope()

    module = Module(id=Identifier("bar"), expr=FunctionApplication(func=Identifier("f"), expr=Int(2)), decls=Declarations(decls=[FunctionDeclaration(scope, id=Identifier("f"), params=[Identifier("x")], expr=BinaryOperator(expr1=Identifier("x"), op=Operator("*"), expr2=Int(3)))])) # module bar = f 2 where { f x = x * 3 }

    check(module, 6, scope)
