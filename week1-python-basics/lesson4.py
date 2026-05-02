#Q4
# def is_even(n):
#     if n % 2 == 0:
#         return True
#     else:
#         return False
# print(is_even(42))
#Q5
products = [
    {"name": "Laptop", "price": 1200},
    {"name": "Phone", "price": 800},
    {"name": "Tablet", "price": 500}]

def most_expensive(list):
    # return max(list, key=lambda x: x['price']).get('name')
    return max(list, key=lambda x: x['price'])
print(most_expensive(products))