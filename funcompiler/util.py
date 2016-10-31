def integer_to_int():
    """Assuming the top of the stack is a reference to an Integer, replace it with an int."""
    return """
    checkcast java/lang/Integer
    invokevirtual java/lang/Integer.intValue()I
    """

def int_to_integer():
    return """
    invokestatic java/lang/Integer.valueOf(I)Ljava/lang/Integer;
    """

def double_to_Double():
    return """
    invokestatic java/lang/Double.valueOf(D)Ljava/lang/Double;
    """

def Double_to_double():
    return """
    checkcast java/lang/Double
    invokevirtual java/lang/Double.doubleValue()D
    """

def print_string():
    return """
    getstatic java/lang/System/out Ljava/io/PrintStream;
    swap
    invokevirtual java/io/PrintStream/print(Ljava/lang/String;)V
    """

def create_stringbuilder():
    return """
    new java/lang/StringBuilder
    dup
    invokespecial java/lang/StringBuilder.<init>()V
    astore_1
    """

def add_to_stringbuilder():
    """Assumes it can use aload_1 to store it, and the top of the stack is the thing to add."""
    return """
    aload_1
    swap
    invokevirtual java/lang/StringBuilder.append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    astore_1
    """
