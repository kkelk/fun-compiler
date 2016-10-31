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
        assert run(module.id.value).lower() == str(expected_output).lower()
        subprocess.run('rm -f *.j *.class', shell=True)
    except:
        if DELETE_ON_FAIL:
            subprocess.run('rm -f *.j *.class', shell=True)
        raise

def test_int():
    # module IntTest = 42
    module = Module(
            id=Identifier("IntTest"),
            expr=Int(42)
    )
    
    check(module, 42)

def test_double():
    # module DoubleTest = 36.0
    module = Module(
            id=Identifier("DoubleTest"),
            expr=Double(36)
    )

    check(module, 36.0)

def test_char():
    # module CharTest = 'a'
    module = Module(
            id=Identifier("CharTest"),
            expr=Char("a")
    )
    
    check(module, 'a')

def test_bool_true():
    # module TrueTest = True
    module = Module(
            id=Identifier("TrueTest"),
            expr=Bool("True")
    )

    check(module, True)

def test_bool_false():
    # module FalseTest = False
    module = Module(
            id=Identifier("FalseTest"),
            expr=Bool("False")
    )

    check(module, False)

def test_zero_args():
    scope = Scope()

    # module ZeroArgTest = x where { x = 3 }
    module = Module(
            id=Identifier("ZeroArgTest"),
            expr=Identifier("x"),
            decls=[FunctionDeclaration(
                scope,
                id=Identifier("x"),
                expr=Int(3)
            )]
    )

    check(module, 3, scope)

def test_ord():
    # module OrdTest = ord('a')
    module = Module(
            id=Identifier("OrdTest"),
            expr=UnaryOperator(
                expr=Char("a"),
                op=Operator("ord")
            )
    )

    check(module, 97)

def test_chr_op():
    # module ChrOpTest = chr(97)
    module = Module(
            id=Identifier("ChrOpTest"),
            expr=UnaryOperator(
                expr=Int(97),
                op=Operator("chr")
            )
    )

    check(module, "a")

def test_char_function():
    scope = Scope()

    # module CharFuncTest = c where { c = 'c' }
    module = Module(
            id=Identifier("CharFuncTest"),
            expr=Identifier("c"),
            decls=[FunctionDeclaration(
                scope,
                id=Identifier("c"),
                expr=Char("c")
            )]
    )

    check(module, "c")

def test_int_operators():
    scope = Scope()

    # module IntOperatorsTest = x + 1 where { x = 3 * 2 }
    module = Module(
            id=Identifier("IntOperatorsTest"),
            expr=BinaryOperator(
                expr1=Identifier("x"),
                op=Operator("+"),
                expr2=Int(1)
            ),
            decls=[FunctionDeclaration(
                scope,
                id=Identifier("x"),
                expr=BinaryOperator(
                    expr1=Int(3),
                    op=Operator("*"),
                    expr2=Int(2)
                )
            )]
    ) 
    check(module, 7, scope)

def test_double_operators():
    scope = Scope()

    # module DoubleOperatorsTest = x + 3.5 where { x = 3.0 * 7.0 }
    module = Module(
            id=Identifier("DoubleOperatorsTest"),
            expr=BinaryOperator(
                expr1=Identifier("x"),
                op=Operator("+"),
                expr2=Double(3.5)
            ),
            decls=[FunctionDeclaration(
                scope,
                id=Identifier("x"),
                expr=BinaryOperator(
                    expr1=Double(3.0),
                    op=Operator("*"),
                    expr2=Double(7.0)
                )
            )]
    )
    
    check(module, 24.5, scope)

def test_one_arg():
    scope = Scope()

    # module OneArgTest = f 2 where { f x = x * 3 }
    module = Module(
            id=Identifier("OneArgTest"),
            expr=FunctionApplication(
                func=Identifier("f"),
                expr=Int(2)
            ),
            decls=[FunctionDeclaration(
                scope,
                id=Identifier("f"),
                params=[Identifier("x")],
                expr=BinaryOperator(
                    expr1=Identifier("x"),
                    op=Operator("*"),
                    expr2=Int(3)
                )
            )]
    ) 

    check(module, 6, scope)

def test_two_args():
    scope = Scope()

    # module TwoArgTest = mul 2.0 5.0 where { mul x y = x * y }
    module = Module(
            id=Identifier("TwoArgTest"),
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

    check(module, 10.0, scope)

"""
def test_three_args():
    scope = Scope()

    # module ThreeArgTest = add 1 2 3 where { add x y z = x + y + z }
    module = Module(
            id=Identifier("ThreeArgTest"),
            expr=FunctionApplication(
                func=FunctionApplication(
                    func=FunctionApplication(
                        func=Identifier("add"),
                        expr=Int(1)
                    ),
                    expr=Int(2)
                ),
                expr=Int(3)
            ),
            decls=[FunctionDeclaration(
                scope,
                id=Identifier("add"),
                params=[Identifier("x"), Identifier("y"), Identifier("z")],
                expr=BinaryOperator(
                    expr1=BinaryOperator(
                        expr1=Identifier("x"),
                        op=Operator("+"),
                        expr2=Identifier("y")
                    ),
                    op=Operator("+"),
                    expr2=Identifier("z")
                )
            ),
            TypeDeclaration(
                scope,
                id=Identifier("add"),
                type=FunctionType(
                    param_type=NamedType(id=Identifier("Int")),
                    return_type=FunctionType(
                        param_type=NamedType(id=Identifier("Int")),
                        return_type=NamedType(id=Identifier("Int"))
                    )
                )
            )]
    )

    check(module, 6, scope)
"""

def test_three_args():
    scope = Scope()

    # module ThreeArgTest = add 1 2 3 where { add x y z = x + y + z }
    module = Module(
            id=Identifier("ThreeArgTest"),
            expr=FunctionApplication(
                func=FunctionApplication(
                    func=FunctionApplication(
                        func=Identifier("add"),
                        expr=Double(1)
                    ),
                    expr=Double(2)
                ),
                expr=Double(3)
            ),
            decls=[FunctionDeclaration(
                scope,
                id=Identifier("add"),
                params=[Identifier("x"), Identifier("y"), Identifier("z")],
                expr=BinaryOperator(
                    expr1=BinaryOperator(
                        expr1=Identifier("x"),
                        op=Operator("+"),
                        expr2=Identifier("y")
                    ),
                    op=Operator("+"),
                    expr2=Identifier("z")
                )
            )]
    )

    check(module, 6.0, scope)

"""
def test_first_class_functions():
    scope = Scope()

    # module FirstClassFunctionTest = increment (add 1) 2 where { increment adder x = adder x ; add x y = x + y }
    module = Module(
            id=Identifier("FirstClassFunctionTest"),
            expr=FunctionApplication(
                func=FunctionApplication(
                    func=Identifier("increment"),
                    expr=FunctionApplication(
                        func=Identifier("add"),
                        expr=Int(1)
                    )
                ),
                expr=Int(2)
            ),
            decls=[
                FunctionDeclaration(
                    scope,
                    id=Identifier("increment"),
                    params=[Identifier("adder"), Identifier("x")],
                    expr=FunctionApplication(
                        func=Identifier("adder"),
                        expr=Identifier("x")
                    )
                ),
                FunctionDeclaration(
                    scope,
                    id=Identifier("add"),
                    params=[Identifier("x"), Identifier("y")],
                    expr=BinaryOperator(
                        expr1=Identifier("x"),
                        op=Operator("+"),
                        expr2=Identifier("y")
                    )
                )
            ]
    )

    check(module, 3, scope)
"""

def test_partial_application():
    scope = Scope()

    # module PartialApplicationTest = add 3 where { add x y = x + y }
    module = Module(
            id=Identifier("PartialApplicationTest"),
            expr=FunctionApplication(
                func=Identifier("add"),
                expr=Int(3)
            ),
            decls=[FunctionDeclaration(
                scope,
                id=Identifier("add"),
                params=[Identifier("x"), Identifier("y")],
                expr=BinaryOperator(
                    expr1=Identifier("x"),
                    op=Operator("+"),
                    expr2=Identifier("y")
                )
            )]
    )

    check(module, 'addFunction with bound parameters: (3)', scope)

def test_lists():
    # module ListTest = [5, 10]
    module = Module(
            id=Identifier("ListTest"),
            expr=Lists(
                exprs=[
                    Int(5),
                    BinaryOperator(expr1=Int(10), op=Operator('-'), expr2=Int(4))
                ]
            )
    )

    check(module, [5, 6])

def test_list_function():
    scope = Scope()

    # module ListFunctionTest = testlist [3, 4] where { testlist x = x }
    module = Module(
            id=Identifier("ListFunctionTest"),
            expr=FunctionApplication(
                func=Identifier("testlist"),
                expr=Lists(
                    exprs=[Int(3), Int(4)]
                )
            ),
            decls=[FunctionDeclaration(
                scope,
                id=Identifier("testlist"),
                params=[Identifier("x")],
                expr=Identifier("x")
            )]
    )

    check(module, [3, 4], scope)

def test_function_type_spec():
    scope = Scope()

    # module FunctionTypeSpecTest = getint 3 where { getint x = x; getint :: Int }
    module = Module(
            id=Identifier("FunctionTypeSpecTest"),
            expr=FunctionApplication(
                func=Identifier("getint"),
                expr=Int(3)
            ),
            decls=[
                FunctionDeclaration(
                    scope,
                    id=Identifier("getint"),
                    params=[Identifier("x")],
                    expr=Identifier("x")),
                TypeDeclaration(
                    scope,
                    id=Identifier("getint"),
                    type=FunctionType(
                        param_type=NamedType(id=Identifier("Int")),
                        return_type=NamedType(id=Identifier("Int"))
                    )
                )
            ]
    )

    check(module, 3, scope)

def test_type_expression():
    # module TypeExpressionTest = 2 + 9 :: Int
    module = Module(
            id=Identifier("TypeExpressionTest"),
            expr=TypeSpecification(
                expr=BinaryOperator(
                    expr1=Int(2),
                    op=Operator("+"),
                    expr2=Int(9)
                ),
                type=NamedType(id=Identifier("Int"))
            )
    )

    check(module, 11)

def test_boolean_int():
    # module BooleanIntTest = 3 == 2 + 1
    module = Module(
            id=Identifier("BooleanIntTest"),
            expr=BinaryOperator(
                expr1=Int(3),
                op=Operator("=="),
                expr2=BinaryOperator(
                    expr1=Int(2),
                    op=Operator("+"),
                    expr2=Int(1)
                )
            )
    )

    check(module, True)

def test_boolean_double():
    # module BooleanDoubleTest = 2.0 + 1.5 < 10.5
    module = Module(
            id=Identifier("BooleanDoubleTest"),
            expr=BinaryOperator(
                expr1=BinaryOperator(
                    expr1=Double(2.0),
                    op=Operator("+"),
                    expr2=Double(1.5)
                ),
                op=Operator("<"),
                expr2=Double(10.5),
            )
    )

    check(module, True)

def test_boolean_lteq():
    # module BooleanLessThanEqualToTest = 4 <= 3
    module = Module(
            id=Identifier("BooleanLessThanEqualToTest"),
            expr=BinaryOperator(
                expr1=Int(4),
                op=Operator("<"),
                expr2=Int(3)
            )
    )

    check(module, False)

def test_not_false():
    # module NotTestFalse = not False
    module = Module(
            id=Identifier("NotTestFalse"),
            expr=UnaryOperator(
                expr=Bool("False"),
                op=Operator("not")
            )
    )

    check(module, True)

def test_not_true():
    # module NotTestTrue = not True
    module = Module(
            id=Identifier("NotTestTrue"),
            expr=UnaryOperator(
                expr=Bool("True"),
                op=Operator("not")
            )
    )

    check(module, False)

def test_data_constructor():
    scope = Scope()

    # module DataConstructorTest = Foo where { data Bar = Foo; }
    module = Module(
            id=Identifier("DataConstructorTest"),
            expr=Constr(id=Identifier("Foo")),
            decls=[DataTypeDeclaration(
                scope,
                id=Identifier("Bar"),
                constrs=[Constr(id=Identifier("Foo"))]
            )]
    )

    check(module, "Foo", scope)

def test_data_equality():
    scope = Scope()

    # module DataEqualityTest = X == X where { data T = X | Y; }
    module = Module(
            id=Identifier("DataEqualityTest"),
            expr=BinaryOperator(
                expr1=Constr(id=Identifier("X")),
                op=Operator("=="),
                expr2=Constr(id=Identifier("X"))
            ),
            decls=[DataTypeDeclaration(
                scope,
                id=Identifier("T"),
                constrs=[
                    Constr(id=Identifier("X")),
                    Constr(id=Identifier("Y"))
                ]
            )]
    )

    check(module, True, scope)

def test_data_inequality():
    scope = Scope()

    # module DataEqualityTest = X == Y where { data T = X | Y; }
    module = Module(
            id=Identifier("DataInequalityTest"),
            expr=BinaryOperator(
                expr1=Constr(id=Identifier("X")),
                op=Operator("=="),
                expr2=Constr(id=Identifier("Y"))
            ),
            decls=[DataTypeDeclaration(
                scope,
                id=Identifier("T"),
                constrs=[
                    Constr(id=Identifier("X")),
                    Constr(id=Identifier("Y"))
                ]
            )]
    )

    check(module, False, scope)
