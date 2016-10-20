class ChildCount():
    def valid(self, value):
        """Should be overriden by subclasses to return a boolean indicating whether the given *value* is a valid number for that instance."""
        raise NotImplementedError

class Exactly(ChildCount):
    def __init__(self, value):
        self.value = value

    def valid(self, value):
        return value == self.value

class GreaterOrEqual(ChildCount):
    def __init__(self, value):
        self.value = value

    def valid(self, value):
        return value >= self.value
