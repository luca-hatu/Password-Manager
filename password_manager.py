import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from cryptography.fernet import Fernet
import os
import json

def load_key():
    return open("secret.key", "rb").read()

def write_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

if not os.path.exists("secret.key"):
    write_key()

key = load_key()
fernet = Fernet(key)

MASTER_PASSWORD_FILE = "master_password.enc"

def set_master_password(password):
    encrypted_password = fernet.encrypt(password.encode()).decode()
    with open(MASTER_PASSWORD_FILE, "w") as file:
        file.write(encrypted_password)

def get_master_password():
    if not os.path.exists(MASTER_PASSWORD_FILE):
        return None
    with open(MASTER_PASSWORD_FILE, "r") as file:
        encrypted_password = file.read()
        return fernet.decrypt(encrypted_password.encode()).decode()

def verify_master_password(input_password):
    stored_password = get_master_password()
    return input_password == stored_password

def add_password(service, username, password):
    data = {}
    if os.path.exists("passwords.json"):
        with open("passwords.json", "r") as file:
            data = json.load(file)
    
    encrypted_password = fernet.encrypt(password.encode()).decode()
    data[service] = {"username": username, "password": encrypted_password}

    with open("passwords.json", "w") as file:
        json.dump(data, file)
    messagebox.showinfo("Success", "Password added successfully.")

def view_passwords(master_password):
    if not verify_master_password(master_password):
        messagebox.showerror("Error", "Incorrect master password.")
        return None

    if not os.path.exists("passwords.json"):
        messagebox.showerror("Error", "No passwords stored yet.")
        return None

    with open("passwords.json", "r") as file:
        data = json.load(file)
    
    passwords = {}
    for service, details in data.items():
        encrypted_password = details["password"]
        decrypted_password = fernet.decrypt(encrypted_password.encode()).decode()
        passwords[service] = {
            "username": details["username"],
            "password": decrypted_password
        }
    return passwords

def delete_password(service, master_password):
    if not verify_master_password(master_password):
        messagebox.showerror("Error", "Incorrect master password.")
        return

    if not os.path.exists("passwords.json"):
        messagebox.showerror("Error", "No passwords stored yet.")
        return

    with open("passwords.json", "r") as file:
        data = json.load(file)
    
    if service in data:
        del data[service]
        with open("passwords.json", "w") as file:
            json.dump(data, file)
        messagebox.showinfo("Success", "Password deleted successfully.")
    else:
        messagebox.showerror("Error", "Service not found.")

def main():
    root = tk.Tk()
    root.title("Password Manager")
    root.geometry("300x200")

    style = ttk.Style()
    style.configure("TButton", font=("Arial", 12))
    style.configure("TLabel", font=("Arial", 12))
    style.configure("TEntry", font=("Arial", 12))

    def setup_master_password():
        if get_master_password() is not None:
            messagebox.showerror("Error", "Master password is already set.")
            return
        password = simpledialog.askstring("Master Password", "Set a new master password:", show='*')
        if password:
            set_master_password(password)
            messagebox.showinfo("Success", "Master password set successfully.")

    def add():
        if get_master_password() is None:
            messagebox.showerror("Error", "Please set the master password first.")
            return
        service = simpledialog.askstring("Service", "Enter the service name:")
        username = simpledialog.askstring("Username", "Enter the username:")
        password = simpledialog.askstring("Password", "Enter the password:", show='*')
        if service and username and password:
            add_password(service, username, password)

    def view():
        if get_master_password() is None:
            messagebox.showerror("Error", "Please set the master password first.")
            return
        master_password = simpledialog.askstring("Master Password", "Enter the master password:", show='*')
        passwords = view_passwords(master_password)
        if passwords is not None:
            view_window = tk.Toplevel(root)
            view_window.title("Stored Passwords")
            view_window.geometry("400x300")
            listbox = tk.Listbox(view_window, font=("Arial", 12))
            listbox.pack(fill=tk.BOTH, expand=True)
            for service, details in passwords.items():
                listbox.insert(tk.END, f"Service: {service}")
                listbox.insert(tk.END, f"  Username: {details['username']}")
                listbox.insert(tk.END, f"  Password: {details['password']}")
                listbox.insert(tk.END, "")

    def delete():
        if get_master_password() is None:
            messagebox.showerror("Error", "Please set the master password first.")
            return
        master_password = simpledialog.askstring("Master Password", "Enter the master password:", show='*')
        service = simpledialog.askstring("Service", "Enter the service name:")
        if service:
            delete_password(service, master_password)

    ttk.Button(root, text="Set Master Password", command=setup_master_password).pack(pady=5)
    ttk.Button(root, text="Add a password", command=add).pack(pady=5)
    ttk.Button(root, text="View passwords", command=view).pack(pady=5)
    ttk.Button(root, text="Delete a password", command=delete).pack(pady=5)
    ttk.Button(root, text="Quit", command=root.quit).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
