class A:
    def __init__(self, b):
        self.b = b

    def get_parameter(self):
        if self.b.get_parameter()[0]:
            return True
        else:
            return False


class T:
    def __init__(self, t):
        self.t = t

    def get_parameter(self):
        return self.t.get_parameter()
