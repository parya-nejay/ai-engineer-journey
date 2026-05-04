with open("greetings.txt", "w") as file:
    file.write("Hello from python!\n")
    file.write("This is line 2.\n")
    file.write("And line 3.\n")
print("File written successfully")
# === READING ===
with open("greetings.txt", "r") as file:
    content = file.read()
print("--- File contents ---")
print(content)
print("--- End ---")

with open("greetings.txt", "r") as file:
    for line in file:
        print(f"Line: {line.strip()}")


# === SAFE FILE READING ===
def read_file_safely(filename):
    try:
        with open(filename, "r") as file:
            return file.read()

    except FileNotFoundError:
        print(f"Error: '{filename}' not found")
        return None
    except PermissionError:
        print(f"Error: no permission to read '{filename}'")
        return None


content = read_file_safely("greetings.txt")
print("Got content:", content[:20] if content else "nothing")

content = read_file_safely("does_not_exist.txt")
print("Got content:", content)


       
