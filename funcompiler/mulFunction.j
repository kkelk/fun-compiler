.class public mulFunction
.super AbstractFunction
.field private param_0 Ljava/lang/Object;
.method public <init>()V
.limit stack 2
aload_0
invokenonvirtual AbstractFunction/<init>()V
aload_0
bipush 2
putfield AbstractFunction.remaining_params I
return
.end method
.method public set_0(Ljava/lang/Object;)V
; Increment the param_number.
; We assume that each set_ will only be called once, at the correct times.
.limit locals 2
.limit stack 10
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
putfield mulFunction.param_0 Ljava/lang/Object;
return
.end method
.method private apply_0(Ljava/lang/Object;)Ljava/lang/Object;
.limit stack 10
.limit locals 2
; Create a new copy of this Function, and set the value passed on it.
new mulFunction
dup
invokespecial mulFunction.<init>()V
dup
aload_1
putfield mulFunction.param_0 Ljava/lang/Object;
areturn
.end method
.method private apply_1(Ljava/lang/Object;)Ljava/lang/Object;
.limit locals 2
.limit stack 10
aload_0
getfield mulFunction.param_0 Ljava/lang/Object;
aload_1
checkcast java/lang/Integer
invokevirtual java/lang/Integer.intValue()I
swap
checkcast java/lang/Integer
invokevirtual java/lang/Integer.intValue()I
swap
imul
new java/lang/Integer
dup_x1
dup_x2
pop
invokespecial java/lang/Integer.<init>(I)V
areturn
.end method
.method public apply(Ljava/lang/Object;)Ljava/lang/Object;
.limit locals 2
.limit stack 10
aload_0
getfield mulFunction.param_number I
dup
getstatic java/lang/System/out Ljava/io/PrintStream;
dup
aload_0
invokevirtual java/io/PrintStream/println(Ljava/lang/Object;)V
swap
invokevirtual java/io/PrintStream/println(I)V

dup
bipush 0
if_icmpeq apply_0
dup
bipush 1
if_icmpeq apply_1
apply_0:
aload_0
aload_1
invokevirtual mulFunction.apply_0(Ljava/lang/Object;)Ljava/lang/Object;
areturn
apply_1:
aload_0
aload_1
invokevirtual mulFunction.apply_1(Ljava/lang/Object;)Ljava/lang/Object;
aconst_null
areturn
.end method
