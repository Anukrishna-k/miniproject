# main.py
from modules.admin import admin_login, admin_menu
from modules.user import user_module_menu
from modules.organizer import organizer_module_menu


def main():
    while True:
        print("\n=== WELCOME TO MULTIPROGRAM MANAGEMENT SYSTEM===")
        print("Select your role:")
        print("1. Admin")
        print("2. User")
        print("3. Event Organizer")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            if admin_login():
                admin_menu()
        elif choice == "2":
            user_module_menu()
        elif choice == "3":
            organizer_module_menu()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("⚠ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
