from funcompiler.funast import Scope
from funcompiler.module import Module
from funcompiler.expression import *
from funcompiler.declaration import *

import subprocess

DELETE_ON_FAIL = False

def run(module_name):
    subprocess.run('java -jar jasmin.jar *.j', shell=True, check=True)
    out = subprocess.check_output(['java', module_name])

    return out.decode('utf-8').strip()

def check(module, expected_output, scope=None):
    """Checks the given Module AST against the expected output (converted to a string)."""
    if not scope:
        scope = Scope()

    module.emit(scope)
    try:
        assert run(module.id.value) == str(expected_output)
        subprocess.run('rm -f *.j *.class', shell=True)
    except:
        if DELETE_ON_FAIL:
            subprocess.run('rm -f *.j *.class', shell=True)
        raise

def test_int():
    module = Module(id=Identifier("inttest"), expr=Int(42)) # module foo = 42
    check(module, 42)

def test_zero_args():
    scope = Scope()

    module = Module(id=Identifier("zeroargstest"), expr=Identifier("x"), decls=[FunctionDeclaration(scope, id=Identifier("x"), expr=Int(3))]) # module bar = x where { x = 3 }
    check(module, 3, scope)

def test_character():
    scope = Scope()

    module = Module(id=Identifier("chartest"), expr=Char("a"))
    check(module, 'a', scope)

def test_character_function():
    scope = Scope()

    module = Module(id=Identifier("charfunctest"), expr=Identifier("c"), decls=[FunctionDeclaration(scope, id=Identifier("c"), expr=Char("c"))])

def test_int_operators():
    scope = Scope()

    module = Module(id=Identifier("intoperatorstest"), expr=BinaryOperator(expr1=Identifier("x"), op=Operator("+"), expr2=Int(1)), decls=[FunctionDeclaration(scope, id=Identifier("x"), expr=BinaryOperator(expr1=Int(3), op=Operator("*"), expr2=Int(2)))]) # module bar = x + 1 where { x = 3 * 2 }
    check(module, 7, scope)

def test_double_operators():
    scope = Scope()

    module = Module(id=Identifier("doubleoperatorstest"), expr=BinaryOperator(expr1=Identifier("x"), op=Operator("+"), expr2=Double(1)), decls=[FunctionDeclaration(scope, id=Identifier("x"), expr=BinaryOperator(expr1=Double(3), op=Operator("*"), expr2=Double(2)))]) # module bar = x + 1 where { x = 3 * 2 }
    check(module, 7.0, scope)

def test_one_arg():
    scope = Scope()

    module = Module(id=Identifier("oneargtest"), expr=FunctionApplication(func=Identifier("f"), expr=Int(2)), decls=[FunctionDeclaration(scope, id=Identifier("f"), params=[Identifier("x")], expr=BinaryOperator(expr1=Identifier("x"), op=Operator("*"), expr2=Int(3)))]) # module bar = f 2 where { f x = x * 3 }

    check(module, 6, scope)

def test_two_args():
    scope = Scope()

    # module bar = mul 2 5 where { mul x y = x * y }
    module = Module(
            id=Identifier("twoargstest"),
            expr=FunctionApplication(
                func=FunctionApplication(
                    func=Identifier("mul"),
                    expr=Double(2)
                ),
                expr=Double(5)
            ),
            decls=[FunctionDeclaration(
                scope,
                id=Identifier("mul"),
                params=[Identifier("x"), Identifier("y")],
                expr=BinaryOperator(
                    expr1=Identifier("x"),
                    op=Operator("*"),
                    expr2=Identifier("y")
                )
            )]
    )

    check(module, 10, scope)
