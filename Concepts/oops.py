class Student:
    school_name = "SSWP"
    def __init__(self,name,age):
        self.name = name
        self.age = age

    def get_details(self):
        print(self.name)
        print(self.age)

    @classmethod
    def update_school(cls,new_name):
        cls.school_name = new_name

    @staticmethod
    def static_me(age):
        if age < 18:
            print(" Not adult")
        else:
            print("Adult")
    
    def __del__(self):
        print("removeddd")
        print(self)
        del self


s1 = Student("Sneha" , 23)
s2 = Student("Vijay" , 13)
print(Student.school_name)
Student.update_school("SSWP_new")
print(Student.school_name)
Student.static_me(s1.age)
Student.static_me(s2.age)

