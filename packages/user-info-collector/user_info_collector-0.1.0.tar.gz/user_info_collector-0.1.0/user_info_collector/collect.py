
def collect_user_info():
    """Collect user information through input fields."""
    name = input("Enter your name: ")
    age = input("Enter your age: ")
    email = input("Enter your email: ")

    # Display collected information
    print("\n--- User Information ---")
    print(f"Name: {name}")
    print(f"Age: {age}")
    print(f"Email: {email}")
