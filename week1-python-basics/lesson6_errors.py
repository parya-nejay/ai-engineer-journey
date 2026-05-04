# number = int("hello") ValueError: invalid literal for int() with base 10: 'hello'
# print(number)
try:
    number = int("hello")
    print(number) 
except ValueError:
    print("That wasn't a valid number!")

print("Program continues running...")

def safe_divide(a, b):
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print(f"Can't divide {a} by zero!")
        return None
    except TypeError:
        print(f"Can't divide {a} by {b} — wrong types")
        return None
print(safe_divide(10, 2)) 
print(safe_divide(10, 0)) 
print(safe_divide(10, "two")) 
print(safe_divide(20, 5)) 

# Future code you'll write in Month 1
# try:
#     respond = call_llm_api(prompt)
#     return response
# except RateLimitError:
#     print("Too many requests, slowing down")
#     wait_and_retry()
# except APIConnectionError:
#     print("Network problem, trying backup")
#     use_backup_api()
# except Exception as e:
#     print(f"Unexpected error: {e}")
#     log_error(e)
