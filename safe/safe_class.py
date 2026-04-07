class Student:
    def __init__(self, name):
        self.name = name

    def introduce(self):
        print("Hi, my name is " + self.name)

s = Student("Jenifer")
s.introduce()