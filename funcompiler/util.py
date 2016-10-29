def integer_to_int():
    """Assuming the top of the stack is a reference to an Integer, replace it with an int."""
    return """
    checkcast java/lang/Integer
    invokevirtual java/lang/Integer.intValue()I
    """

def int_to_integer():
    return """
    new java/lang/Integer
    dup_x1
    dup_x2
    pop
    invokespecial java/lang/Integer.<init>(I)V
    """

def double_to_Double():
    return """
    new java/lang/Double
    dup_x1
    dup_x2
    pop
    invokespecial java/lang/Double.<init>(D)V
    """

def Double_to_double():
    return """
    checkcast java/lang/Double
    invokevirtual java/lang/Double.doubleValue()D
    """
