def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Error: Division by zero"
    return a / b

def calculator():
    """
    This module provides a simple command-line calculator application.

    Functions:
        calculator():
            A function that serves as the main entry point for the calculator application.
            It allows users to perform basic arithmetic operations such as addition, 
            subtraction, multiplication, and division. The function handles user input, 
            validates it, and performs the selected operation. It also provides error 
            handling for invalid inputs and division by zero.
    """
    print("Welcome to the Calculator App!")
    print("Select operation:")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")

    while True:
        choice = input("Enter choice (1/2/3/4): ")
        if choice in ['1', '2', '3', '4']:
            try:
                num1 = float(input("Enter first number: "))
                num2 = float(input("Enter second number: "))
            except ValueError:
                print("Invalid input. Please enter numeric values.")
                continue

            if choice == '1':
                print(f"The result is: {round(add(num1, num2), 2)}")
            elif choice == '2':
                print(f"The result is: {round(subtract(num1, num2), 2)}")
            elif choice == '3':
                print(f"The result is: {round(multiply(num1, num2), 2)}")
            elif choice == '4':
                result = divide(num1, num2)
                if isinstance(result, str):  # Check for error message
                    print(result)
                else:
                    print(f"The result is: {round(result, 2)}")
        else:
            print("Invalid choice. Please select a valid operation.")

        next_calculation = input("Do you want to perform another calculation? (yes/no): ")
        if next_calculation.lower() != 'yes':
            print("Goodbye!")
            break

if __name__ == "__main__":
    calculator()