from cryptography.fernet import Fernet
import os
import json

def load_key():
    """Load the key from the current directory named `secret.key`"""
    return open("secret.key", "rb").read()

def write_key():
    """Generate a key and save it into a file"""
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

if not os.path.exists("secret.key"):
    write_key()

key = load_key()
fernet = Fernet(key)

def add_password(service, username, password):
    data = {}
    if os.path.exists("passwords.json"):
        with open("passwords.json", "r") as file:
            data = json.load(file)
    
    encrypted_password = fernet.encrypt(password.encode()).decode()
    data[service] = {"username": username, "password": encrypted_password}

    with open("passwords.json", "w") as file:
        json.dump(data, file)
    print("Password added successfully.")

def view_password(service):
    if not os.path.exists("passwords.json"):
        print("No passwords stored yet.")
        return

    with open("passwords.json", "r") as file:
        data = json.load(file)
    
    if service in data:
        encrypted_password = data[service]["password"]
        decrypted_password = fernet.decrypt(encrypted_password.encode()).decode()
        print(f"Service: {service}")
        print(f"Username: {data[service]['username']}")
        print(f"Password: {decrypted_password}")
    else:
        print("Service not found.")

def delete_password(service):
    if not os.path.exists("passwords.json"):
        print("No passwords stored yet.")
        return

    with open("passwords.json", "r") as file:
        data = json.load(file)
    
    if service in data:
        del data[service]
        with open("passwords.json", "w") as file:
            json.dump(data, file)
        print("Password deleted successfully.")
    else:
        print("Service not found.")

def main():
    while True:
        print("1. Add a password")
        print("2. View a password")
        print("3. Delete a password")
        print("4. Quit")
        choice = input("Choose an option: ")

        if choice == "1":
            service = input("Enter the service name: ")
            username = input("Enter the username: ")
            password = input("Enter the password: ")
            add_password(service, username, password)
        elif choice == "2":
            service = input("Enter the service name: ")
            view_password(service)
        elif choice == "3":
            service = input("Enter the service name: ")
            delete_password(service)
        elif choice == "4":
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
