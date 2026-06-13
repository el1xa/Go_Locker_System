from studentMode import LockerRentalSystem
from adminMode import AdminSystem


def main_menu():
    # Ask the user if they want to start the program
    varDecision1 = input("Do you want to start the Program? (Y/N): ").lower()
    if varDecision1 != 'y':
        print("Exiting the program.")
        return  # Exit if the user doesn't want to start the program

    while True:  # Start the main menu loop if the user confirmed they want to start
        print("\n++++ Welcome to GO 'MOBILE' Locker ++++")
        print("A. Admin Mode")
        print("B. Student Mode")
        print("0. Exit")

        user_input = input("Enter your choice: ").capitalize()

        if user_input == 'A':
            admin_system = AdminSystem()  # Instantiate Admin system
            admin_system.run()  # Call its `run()` method
        elif user_input == 'B':
            student_system = LockerRentalSystem()  # Instantiate Student system
            student_system.run()  # Call its `run()` method
        elif user_input == '0':
            print("Exiting...")
            break  # Exit the loop and end the program
        else:
            print("Invalid input. Try again.")


# This ensures that main_menu() is only executed if this file is run directly
if __name__ == "__main__":
    main_menu()
