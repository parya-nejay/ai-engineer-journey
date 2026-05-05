# from fastapi import FastAPI
# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"message": "Hello, World!"}

# @app.get("/employees")
# def get_employees():
#     return [
#         {"id": 1, "name": "Alice", "salary": 50000},
#         {"id": 2, "name": "Bob", "salary": 60000},
#         {"id": 3, "name": "Charlie", "salary": 70000},
#     ]
# @app.get("/employees/{employee_id}")
# def get_employee(employee_id: int):
#     employees = {
#          1: {"id": 1, "name": "Alice", "salary": 50000},
#         2: {"id": 2, "name": "Bob", "salary": 60000},
#         3: {"id": 3, "name": "Charlie", "salary": 70000},
#     }
#     return employees.get(employee_id, {"error":"Not found"})

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel

# app = FastAPI()


# # === Pydantic model — defines the shape of an Employee ===
# class Employee(BaseModel):
#     id: int
#     name: str
#     salary: int


# # === In-memory database (for now) ===
# employees_db = {
#     1: {"id": 1, "name": "Alice", "salary": 50000},
#     2: {"id": 2, "name": "Bob", "salary": 60000},
#     3: {"id": 3, "name": "Charlie", "salary": 70000},
# }


# # === GET endpoints (read) ===

# @app.get("/")
# def read_root():
#     return {"message": "Hello, World!"}


# @app.get("/employees")
# def get_employees():
#     return list(employees_db.values())


# @app.get("/employees/{employee_id}")
# def get_employee(employee_id: int):
#     if employee_id not in employees_db:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     return employees_db[employee_id]


# # === POST endpoint (create) ===

# @app.post("/employees")
# def create_employee(employee: Employee):
#     if employee.id in employees_db:
#         raise HTTPException(status_code=400, detail="Employee with this ID already exists")
#     employees_db[employee.id] = employee.model_dump()
#     return employees_db[employee.id]


# # === PUT endpoint (update) ===

# @app.put("/employees/{employee_id}")
# def update_employee(employee_id: int, employee: Employee):
#     if employee_id not in employees_db:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     employees_db[employee_id] = employee.model_dump()
#     return employees_db[employee_id]


# # === DELETE endpoint ===

# @app.delete("/employees/{employee_id}")
# def delete_employee(employee_id: int):
#     if employee_id not in employees_db:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     deleted = employees_db.pop(employee_id)
#     return {"deleted": deleted}


import json
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

DB_FILE = "employees.json"


# === Pydantic model ===
class Employee(BaseModel):
    id: int
    name: str
    salary: int


# === Load/save helpers ===

def load_db():
    if not os.path.exists(DB_FILE):
        return {
            1: {"id": 1, "name": "Alice", "salary": 50000},
            2: {"id": 2, "name": "Bob", "salary": 60000},
            3: {"id": 3, "name": "Charlie", "salary": 70000},
        }
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            return {int(k): v for k, v in data.items()}
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)


# === Initialize on startup ===
employees_db = load_db()


# === Endpoints ===

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/employees")
def get_employees():
    return list(employees_db.values())


@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    if employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employees_db[employee_id]


@app.post("/employees")
def create_employee(employee: Employee):
    if employee.id in employees_db:
        raise HTTPException(status_code=400, detail="Employee with this ID already exists")
    employees_db[employee.id] = employee.model_dump()
    save_db(employees_db)
    return employees_db[employee.id]


@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, employee: Employee):
    if employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Employee not found")
    employees_db[employee_id] = employee.model_dump()
    save_db(employees_db)
    return employees_db[employee_id]


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    if employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Employee not found")
    deleted = employees_db.pop(employee_id)
    save_db(employees_db)
    return {"deleted": deleted}