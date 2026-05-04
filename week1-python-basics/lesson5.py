class Employee: #define the class
    def __init__(self, name, salary): # ② The constructor
       self.name = name               # ③ Save attributes on the object
       self.salary = salary

    def greet(self):                   # ④ A method
        return f"Hi, I'm {self.name} and I earn {self.salary}"
    
    def give_raise(self, amount):
        self.salary = self.salary + amount
        return self.salary
    
    def is_well_paid(self):
        return self.salary > 55000
    
    def __str__(self):
        return f"Employee(name={self.name}, salary={self.salary})"
        
    
emp1 = Employee("Alice", 50000)
emp2 = Employee("Bob", 60000)

print(emp1.greet())
print(emp2.greet())
print(emp1.name)
print(emp1.salary)
print(emp1.is_well_paid())          # False — Alice earns 50000
print(emp2.is_well_paid())          # True — Bob earns 60000

emp1.give_raise(10000)              # Alice gets a 10k raise
print(emp1.salary)                  # 60000
print(emp1.is_well_paid())          # Now True
print(emp1)
