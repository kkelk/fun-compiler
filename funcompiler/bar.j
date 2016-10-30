.class public bar
.super java/lang/Object
.method public static module()Ljava/lang/Object;
.limit stack 10
new mulFunction
dup
invokespecial mulFunction.<init>()V
checkcast AbstractFunction
dup
ldc 2
new java/lang/Integer
dup_x1
dup_x2
pop
invokespecial java/lang/Integer.<init>(I)V
invokevirtual AbstractFunction.apply(Ljava/lang/Object;)Ljava/lang/Object;
checkcast AbstractFunction
dup
ldc 5
new java/lang/Integer
dup_x1
dup_x2
pop
invokespecial java/lang/Integer.<init>(I)V
invokevirtual AbstractFunction.apply(Ljava/lang/Object;)Ljava/lang/Object;
areturn
.end method
.method public static main([Ljava/lang/String;)V
.limit stack 2
getstatic java/lang/System/out Ljava/io/PrintStream;
invokestatic bar.module()Ljava/lang/Object;
invokevirtual java/io/PrintStream/println(Ljava/lang/Object;)V
return
.end method