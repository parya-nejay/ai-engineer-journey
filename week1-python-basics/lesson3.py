# ===== LISTS (like List<T> in C#) =====
fruits = ["apple", "banana", "cherry"] #list of strings
print(fruits)
print(fruits[0]) #access first element
print(fruits[-1]) #access last element
print(len(fruits)) #length of list
#add to list remove modify list
fruits.append("orange") #add to end of list
fruits.remove("banana") #remove from list
print(fruits)

#Slicing - python's supperpower
numbers = [10, 20, 30, 40, 50, 60]
print(numbers[1:4])
print(numbers[:3]) #first 3 elements
print(numbers[3:]) #from index 3 to end
print(numbers[-2:]) #last 2 elements
# ===== DICTIONARIES (like Dictionary<TKey, TValue> in C#) ====
person = {
    "name": "Alice",
    "age": 25,
    "is_developer": True
}
print(person)
print(person["name"])
print(person["age"])
#print(person["city"]) = "Tehran" 
person["city"] = "Tehran" 
print(person)
# Safe access (like TryGetValue in C#)
city = person.get("city", "Unknown") #returns "Unknown" if key not found
Country = person.get("country", "Unknown") #returns "Unknown" if key not found
print(city)

# ===== TUPLES (like ValueTuple in C#, but more common) =====
point = (10, 20) #tuple of two integers
x, y = point #unpacking tuple
print(f"x={x}, y={y}")
# Functions can return multiple values via tuples (very common in Python)
def get_min_max(nums):
    return min(nums), max(nums)
    low, high = get_min_max([3, 1, 4, 1, 5])
    print(f"min={low}, max={high}")

# ===== LIST COMPREHENSIONS — Python's killer feature =====
# C#: var squares = numbers.Select(n => n * n).ToList();
squares = [n * n for n in numbers]
print(squares)

# C#: var evens = numbers.Where(n => n % 2 == 0).ToList();
evens = [n for n in numbers if n % 2 == 0]
print(evens) 

# Combined: square only the even ones
even_squares = [n * n for n in numbers if n % 2 == 0]
print(even_squares)

# Exercise: 
# Given this list of dicts (like a list of objects in C#)
employees = [
    {"name": "Alice", "salary": 50000, "department": "Engineering"},
    {"name": "Bob", "salary": 60000, "department": "Sales"},
    {"name": "Charlie", "salary": 70000, "department": "Engineering"},
    {"name": "Diana", "salary": 55000, "department": "Marketing"},
]

# TODO 1: Print only the names of employees in Engineering
# (Hint: use a list comprehension with an `if`)

# TODO 2: Calculate the total salary of all employees
# (Hint: there's a built-in function called sum())

# TODO 3: Find the employee with the highest salary
# (Hint: max() with a key argument — google "python max with key" if stuck

def get_engineering_employees(employees): return [employee["name"] for employee in employees if employee["department"] == "Engineering"]
print(get_engineering_employees(employees))

def get_total_salary(employees): return sum(employee["salary"] for employee in employees)
print(get_total_salary(employees))

def get_employee_with_salary(employees): return max(employees, key=lambda e: e["salary"])
print(get_employee_with_salary(employees))
