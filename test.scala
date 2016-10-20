object HelloWorld {
   def safeStringOp(s: String, f: String => String) = {
        if (s != null) f(s) else s
      }

    def reverser(s: String) = s.reverse

    def main(args: Array[String]): Unit = {
        safeStringOp("Ready", reverser)
    }
}
