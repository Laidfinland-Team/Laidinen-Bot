class A:
    def __init__(self):
        self.b = 5
        
a = A()
c = []

c.append(a)
a.b = 6
print(c[0].b)
