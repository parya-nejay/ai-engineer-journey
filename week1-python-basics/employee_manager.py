# Stores employees as objects (using your Employee class)


class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def __str__(self):
        return f"{self.name},{self.salary}"


def save_employees(employees, filename):
    try:
        with open(filename, "w") as file:
            for emp in employees:
                file.write(str(emp) + "\n")
            print(f"Saved {len(employees)} employees to {filename}")
    except Exception as e:
        print(f"Error saving:{e}")


def load_employees(filename):
    """Load employees from a file. Returns a list of Employee objects."""
    employees = []
    try:
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if line:
                    name, salary = line.split(",")
                    employees.append(Employee(name, int(salary)))
        print(f"Loaded {len(employees)} employees from {filename}")
    except FileNotFoundError:
        print(f"File '{filename}' not found, starting fresh")
    except ValueError as e:
        print(f"File is corrupted: {e}")
    return employees

# === Test it ===


team = [
    Employee("Alice", 50000),
    Employee("Bob", 60000),
    Employee("Charlie", 70000),
]
save_employees(team, "team.txt")
loaded_team = load_employees("team.txt")
print("\n--- Loaded team ---")
for emp in loaded_team:
    print(emp)

print("\n--- Trying missing file ---")
missing = load_employees("nonexistent.txt")
print(f"Got {len(missing)} employees")
