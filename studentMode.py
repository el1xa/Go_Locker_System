import json
import time
import sys
from datetime import datetime

# Cannot change file permission to 'w' from the beginning or else, json file will be reset
# Can only change permission to 'w' within the function itself
class LockerRentalSystem:
    def __init__(self):
        # Load data from JSON file
        with open('appendixA.json', 'r') as file:
            self.data = json.load(file)

    def display_menu(self):
        print("\n++++ Go Locker – Operations ++++"
              "\n1. Rent a locker"
              "\n2. Request move"
              "\n3. Return locker"
              "\n4. Enquire locker location"
              "\n5. View usage report"
              "\n6. Check Balance/Top-Up"
              "\n0. Exit")

    # Checks if student exist
    def find_student(self, student_id):
        for student in self.data['students']:
            if student['studentID'] == student_id:
                return student
        return None

    # Checks if locker exists
    def find_locker(self, locker_id):
        for locker in self.data['lockers']:
            if locker['lockerID'] == locker_id:
                return locker
        return None

    # Checks if the locker is available (option 1)
    def available_locker(self):
        for locker in self.data['lockers']:
            if locker['status'] == "Available":
                return locker
        return None

    def get_rental_id_counter(self):
        # Combine both rentals and usedRentalIDs into one list to check all used rentalIDs
        used_rental_ids = self.data["usedRentalIDCounters"]

        # Start at 20000 if no rentalIDs are used
        next_rental_id = 2400000

        # Find the next available rentalID
        while str(next_rental_id) in used_rental_ids:
            next_rental_id += 1  # Increment until a free rentalID is found

        return str(next_rental_id)

    # for delay in response (move)
    def updating_response(self, messages, delay=1):
        for message in messages:
            # It clears the line and prints the new message
            sys.stdout.write('\r' + ' ' * 80)
            sys.stdout.write('\r' + message)
            sys.stdout.flush()  # Ensures that the character is printed immediately
            time.sleep(delay)  # Wait for the specified delay
        print()  # Moves to the next line after the final message

    # Functions for the different options start here:

    # Rental of Locker
    def rent_locker(self):
        student_id = input("Enter Student ID: ")
        student = self.find_student(student_id)

        if not student:
            print("Invalid Student ID.")
            return

        rented_lockers = [locker for locker in self.data['lockers'] if locker.get('rentalID') == student_id]
        if len(rented_lockers) >= 2:
            print("Sorry, you are already renting 2 lockers.")
            #Displaying previous rental details
            for locker in rented_lockers:
                print(f"---------------------------------------------------------")
                print(f"Locker allocated: {locker['lockerID']} \tLocation: {locker['location']}")
                print(f"Rental ID: {locker['rentalIDCounter']}")
                print(f"Start date: {locker['startDate']}")
            print(f"---------------------------------------------------------")
            return

        locker = self.available_locker()
        if locker:
            if float(student["Account"]) < self.data['rentalFee']:
                print("Insufficient balance to rent the locker.")
                return

            # Changes to Json if locker can be rented
            new_rental_id_counter = self.get_rental_id_counter()
            locker['status'] = "Occupied"
            locker['rentalID'] = student_id
            locker['startDate'] = datetime.now().strftime("%d-%b-%Y")
            locker['endDate'] = "" #reset
            locker['rentalIDCounter'] = new_rental_id_counter
            locker['startDateTime'] = datetime.now().strftime("%H:%M")  # for Function5
            student["Account"] = "{:.2f}".format(float(student["Account"]) - self.data['rentalFee'])  # Deduct rental charge
            print(f"---------------------------------------------------------")
            print(f"Locker allocated: {locker['lockerID']} \tLocation: {locker['location']}")
            print(f"Rental ID: {locker['rentalIDCounter']}")
            print(f"Start date: {locker['startDate']}")
            print(f"${self.data['rentalFee']:.2f} is charged to your account.")
            print(f"---------------------------------------------------------")

            # Append to moveHistory
            move_record = {
                'timestamp': datetime.now().strftime("%d-%b-%Y"),
                'timestampTime': datetime.now().strftime("%H:%M"),
                'operation': "Locker rental",
                'from': locker['previousLocation'],
                'to': locker['location'],
                'userID': locker['rentalID'],
                'rentalIDCounter1': locker['rentalIDCounter']
            }
            locker.setdefault('moveHistory', []).append(move_record)

            #Append all the used rentalIDCounters into rentalIDCounterList in Json file
            self.data['usedRentalIDCounters'].append(new_rental_id_counter)

            # Save the updated data back to the JSON file
            with open('appendixA.json', 'w') as file:
                json.dump(self.data, file, indent=4)
        else:
            print("No available lockers at the moment.")

    # Request Move:
    def request_move(self):
        # Check if Student Exists:
        student_id = input("Enter Student ID: ")
        student = self.find_student(student_id)
        if not student:
            print("Invalid Student ID.")
            return

        # If Student exists: Check if there is enough money for a move:
        if not float(student['Account']) > self.data['movingFee']:
            print("Insufficient balance for move.")
            return

        # Check if Locker exists
        locker_id = input("Enter Locker ID: ")
        locker = self.find_locker(locker_id)
        if not locker:
            print("Invalid Locker ID.")
            return

        # If locker is not rented to user or anyone else:
        if locker['status'] == 'Available' or locker['rentalID'] != student_id:
            print(f"Sorry, {locker_id} is not your locker.")
            return

        # If locker is rented to user:
        print(f"---------------------------------------------------------")
        print(f"Locker allocated: {locker['lockerID']} \tLocation: {locker['location']}")
        print(f"Rental ID: {locker['rentalIDCounter']}")
        print(f"Start date: {locker['startDate']}")
        print(f"---------------------------------------------------------")

        # Prompt for user to input station code he wants to move the locker to:
        user_input_location = input("\nEnter Station code to move to: ")

        # Check if the user_input_location is the same as the current location:
        currentLocationHolder = locker['location']
        if user_input_location == currentLocationHolder or user_input_location == currentLocationHolder[:-7]:
            print(f"Locker is already at {user_input_location}")
            return

        # If the user wants to move back to the Central store:
        if user_input_location == "Central store":
            locker['previousLocation'] = locker['location']  # Track previous location
            locker['location'] = "Central store"  # Update the current location
            student['Account'] = f"{float(student['Account']) - self.data['movingFee']:.2f}"  # Update the Student's Account balance

            # For station to station/station to Central store locker move, need to update "status" of slot in previousLocation to "Available":
            for station in self.data['stations']:
                for slot in station['slots']:
                    if locker['previousLocation'] == slot["slotID"] and slot["statusID"] == "Occupied":
                        slot['statusID'] = "Available"

            # Append to moveHistory
            move_record = {
                'timestamp': datetime.now().strftime("%d-%b-%Y"),
                'timestampTime': datetime.now().strftime("%H:%M"),
                'operation': f"Move to {locker['location']}",
                'from': locker['previousLocation'],
                'to': locker['location'],
                'userID': locker['rentalID'],
                'rentalIDCounter1': locker['rentalIDCounter']
            }
            locker.setdefault('moveHistory', []).append(move_record)

            # Updating messages for the move:
            print(f"Locker moving to {locker['location']}")
            print(f"---------------------------------------------------------")
            messages = [
                f"Locker allocated: {locker['lockerID']} \tLocation: In transit... ",
                f"Locker allocated: {locker['lockerID']} \tLocation: Still in transit...",
                f"Locker allocated: {locker['lockerID']} \tLocation: Almost done...",
                f"Locker allocated: {locker['lockerID']} \tLocation: {locker['location']}"
            ]
            # Call updating_response function:
            self.updating_response(messages, 1)
            print(f"Rental ID Counter: {locker['rentalIDCounter']} \nStart date: {locker['startDate']}")
            print(f"${self.data['movingFee']:.2f} is charged to your account.")
            print(f"---------------------------------------------------------")
            return

        else:
            pass

        # If the user_input_location != "Central store":
        # Checking if the destination is valid: (Station must exist and be open)
        station_exists = False
        for station in self.data['stations']:
            if user_input_location == station['stationCode'] and station['status'] == "Open":
                station_exists = True

        if not station_exists:
            print("Invalid station code or station is closed.")
            return

        # Checking if there is an available slot in the specified station: (Slot must be "Available")
        for station in self.data['stations']:
            if station['stationCode'] == user_input_location:
                # Find all available slots in the matched station
                available_slot = [slot for slot in station['slots'] if slot['statusID'] == 'Available']
                break  # Exit loop once station is found

        if not available_slot:
            print("No available slots at this station.")
            return

        # If the locker is going to be moved:
        # Update the locker's previous and current location to track every move for Function5
        locker['previousLocation'] = locker['location']  # Track the previous location

        # Assign the new locker slot (taking the first available slot)
        new_slot = available_slot[0]
        locker['location'] = new_slot['slotID']  # Assign the new locker slot
        new_slot['statusID'] = "Occupied"  # Mark the slot as "Occupied"
        student['Account'] = f"{float(student['Account']) - self.data['movingFee']:.2f}"  # Update the Student's Account balance

        # For station to station locker move, need to update "status" of slot in previousLocation to "Available":
        for station in self.data['stations']:
            for slot in station['slots']:
                if locker['previousLocation'] == slot["slotID"] and slot["statusID"] == "Occupied":
                    slot['statusID'] = "Available"

        # Append to moveHistory
        move_record = {
            'timestamp': datetime.now().strftime("%d-%b-%Y"),
            'timestampTime': datetime.now().strftime("%H:%M"),
            'operation': f"Move to {locker['location']}",
            'from': locker['previousLocation'],
            'to': locker['location'],
            'userID': locker['rentalID'],
            'rentalIDCounter1': locker['rentalIDCounter']
        }
        locker.setdefault('moveHistory', []).append(move_record)

        # Updating messages for the move:
        print(f"Locker moving to {locker['location']}")
        print(f"---------------------------------------------------------")
        messages = [
            f"Locker allocated: {locker['lockerID']} \tLocation: In transit... ",
            f"Locker allocated: {locker['lockerID']} \tLocation: Still in transit...",
            f"Locker allocated: {locker['lockerID']} \tLocation: Almost done...",
            f"Locker allocated: {locker['lockerID']} \tLocation: {locker['location']}"
        ]
        # Call updating_response function:
        self.updating_response(messages, 1)
        print(f"Rental ID Counter: {locker['rentalIDCounter']} \nStart date: {locker['startDate']}")
        print(f"${self.data['movingFee']:.2f} is charged to your account.")
        print(f"---------------------------------------------------------")

        # Save the updated data back to the JSON file
        with open('appendixA.json', 'w') as file:
            json.dump(self.data, file, indent=4)

    # Return locker
    def return_locker(self):
        student_id = input("Enter Student ID: ")
        student = self.find_student(student_id)
        if not student:
            print("Invalid Student ID.")
            return

        locker_id = input("Enter Locker ID: ")
        locker = self.find_locker(locker_id)
        if not locker:
            print("Invalid Locker ID.")
            return

        # Check if the locker is rented and belongs to the student, if not True:
        if locker['status'] == 'Available' or locker['rentalID'] != student_id:
            print("You cannot return this locker as it was not rented by you or it's not rented.")
            return

        # Display locker details
        print(f"---------------------------------------------------------")
        print(f"Locker allocated: {locker['lockerID']} \tLocation: {locker['location']}")
        confirm = input("Are you sure you want to return this locker? (yes/no): ")

        if confirm.lower() != 'yes':
            print("Locker return canceled.")
            return

        #Updates if the return is successful:
        locker['status'] = 'Available'
        locker['rentalID'] = ""
        locker['endDate'] = datetime.now().strftime("%d-%b-%Y")

        locker['previousLocation'] = locker['location'] #Track previousLocation
        locker['location'] = "Central store" #Update the new location

        # For station to station locker move, need to update "status" of slot in previousLocation to "Available":
        for station in self.data['stations']:
            for slot in station['slots']:
                if locker['previousLocation'] == slot["slotID"] and slot["statusID"] == "Occupied":
                    slot['statusID'] = "Available"

        #Display if return is successful:
        print(f"---------------------------------------------------------")
        print(f"Locker allocated: {locker['lockerID']} \tLocation: {locker['previousLocation']}")
        print(f"Rental ID: {locker['rentalIDCounter']}") #Not cleared, when rented again, it will be replaced by new one
        print(f"Start date: {locker['startDate']}") #Not cleared, when rented again, it will be replaced by new one
        print(f"End date: {locker['endDate']}.") #Not cleared, when rented again, it will be replaced by new one
        print(f"Moving locker back to {locker['location']}.")
        print(f"---------------------------------------------------------")

        #Append moveHistory
        move_record = {
            'timestamp': datetime.now().strftime("%d-%b-%Y"),
            'timestampTime': datetime.now().strftime("%H:%M"),
            'operation': "Return Locker",
            'from': locker['previousLocation'],
            'to': locker['location'],
            'userID': locker['rentalID'],
            'rentalIDCounter1': f"{locker['rentalIDCounter']}"
        }
        locker.setdefault('moveHistory', []).append(move_record)

        # Display Charge Report:
        # Get rental fee:
        rental_charge = self.data['rentalFee']
        # Calculation for Move Charges
        charge_per_move = self.data['movingFee']

        lockerMoves = []
        for move in locker.get('moveHistory', []):
            operation = move.get('operation')
            if "rentalIDCounter1" in move and 'operation' in move:
                if move.get("rentalIDCounter1") == locker.get('rentalIDCounter') and operation[:4] == "Move" :
                    lockerMoves.append(move)

        move_count = len(lockerMoves)
        move_charges = charge_per_move * move_count
        # Calculation for Total Charges:
        total_charges = move_charges + rental_charge

        print(f"Rental Charge: ${rental_charge:.2f}")
        print(f"Move Charges: ${move_charges:.2f} ({move_count} moves)")
        print(f"Total charges for this rental: ${total_charges:.2f}")
        print("-------------------------------------------------------------")

        # Save the updated data back to the JSON file
        with open('appendixA.json', 'w') as file:
            json.dump(self.data, file, indent=4)

    # enquiring the locker location only if you have rented the locker
    def enquire_locker_location(self):
        student_id = input("Enter Student ID: ")
        student = self.find_student(student_id)

        if not student:
            print("Invalid Student ID.")
            return

        rented_lockers = [locker for locker in self.data['lockers'] if locker.get('rentalID') == student_id]
        if not rented_lockers:
            print("No rental records.")
            return

        for locker in rented_lockers:
            print(f"---------------------------------------------------------")
            print(f"Locker allocated: {locker['lockerID']} \tLocation: {locker['location']}")
            print(f"Rental ID: {locker['rentalIDCounter']}")
            print(f"Start date: {locker['startDate']}")
        print(f"---------------------------------------------------------")

    # View Usage Report (has 2 parts)
    def view_usage_report(self):
        student_id = input("Enter Student ID: ")
        student = self.find_student(student_id)

        if not student:
            print("Invalid Student ID.")
            return

        # checking for rental records
        rental_records = [locker for locker in self.data['lockers'] if locker.get('rentalID') == student_id]

        if not rental_records:
            print("No rental records.")
            return

        # If rental records are found:
        for locker in rental_records:
            print(f"---------------------------------------------------------")
            print(f"Locker allocated: {locker['lockerID']} \tLocation: {locker['location']}")
            print(f"Rental ID: {locker['rentalIDCounter']}")
            print(f"Start date: {locker['startDate']}")
        print(f"---------------------------------------------------------")

        # Part 2: Prompt for Rental ID to view usage
        rental_id = input("Enter Rental ID to view usage: ")
        records_for_rental = [locker for locker in self.data['lockers'] if locker.get("rentalIDCounter") == rental_id]

        if not records_for_rental:
            print("Invalid Rental ID or You do not have access to this record's details.")
            return

        # You can assume there will be one locker for the rental ID
        locker = records_for_rental[0]  # Get the first locker from the records

        # Formatting the report if rental_id matches:
        # (UpperDivision)
        border = ""
        filler = " "
        rowStr = "" + border
        rowStr += "".center(14, filler) + border
        rowStr += "".center(8, filler) + border
        rowStr += "".center(28, filler) + border
        rowStr += "".center(12, filler) + border

        # (Text 1st Row)
        rowStr += "\n"
        filler = " "
        rowStr += "" + border
        rowStr += "Date".ljust(14, filler) + border
        rowStr += "Time".ljust(8, filler) + border
        rowStr += "Operation".center(28, filler) + border
        rowStr += "Student ID".ljust(12, filler) + border

        # (Bottom division)
        rowStr += "\n"
        filler = "-"
        rowStr += "" + border
        rowStr += "".ljust(14, filler) + border
        rowStr += "".ljust(8, filler) + border
        rowStr += "".ljust(28, filler) + border
        rowStr += "".ljust(12, filler) + border

        # (Text 2nd row)
        rowStr += "\n"
        filler = " "
        rowStr += "" + border
        rowStr += f"{locker['startDate']}".ljust(14, filler) + border
        rowStr += f"{locker['startDateTime']}".ljust(8, filler) + border
        rowStr += "Locker Rental".ljust(28, filler) + border
        rowStr += f"{locker['rentalID']}".ljust(12, filler) + border
        print(rowStr)

        # If there are Move Records: sendHelp for my brains
        if 'moveHistory' in locker:
            printed_moves = set()  # To keep track of printed moves (So that every move is only printed once)
            for move in locker['moveHistory']:
                operation = move.get('operation')

                # Check for the necessary keys and conditions
                if "rentalIDCounter1" in move and 'operation' in move:
                    if move.get("rentalIDCounter1") == locker.get('rentalIDCounter') and operation != "Locker Rental" and operation != "Suspended":
                        move_key = (move['timestampTime'], move['to'])  # Create a unique key for each move
                        if move_key not in printed_moves:
                            printed_moves.add(move_key)  # Add the move key to the set

                            # Construct the row string for output
                            rowStr = "" + border  # Reset rowStr for new entry
                            rowStr += "" + border
                            rowStr += f"{move['timestamp']}".ljust(14, filler) + border
                            rowStr += f"{move['timestampTime']}".ljust(8, filler) + border
                            rowStr += f"Move to {move['to']}".ljust(28, filler) + border
                            rowStr += f"{locker['rentalID']}".ljust(12, filler) + border

                            print(rowStr)  # Print the constructed row string

        #Display Charge Report:
        # Get rental fee:
        rental_charge = self.data['rentalFee']
        # Calculation for Move Charges
        charge_per_move = self.data['movingFee']

        lockerMoves = []
        for move in locker.get('moveHistory', []):
            operation = move.get('operation')
            if "rentalIDCounter1" in move and 'operation' in move:
                if move.get("rentalIDCounter1") == locker.get('rentalIDCounter') and operation[:4] == "Move":
                    lockerMoves.append(move)

        move_count = len(lockerMoves)
        move_charges = charge_per_move * move_count
        # Calculation for Total Charges:
        total_charges = move_charges + rental_charge

        print(f"Rental Charge: ${rental_charge:.2f}")
        print(f"Move Charges: ${move_charges:.2f} ({move_count} moves)")
        print(f"Total charges for this rental: ${total_charges:.2f}")
        print("-------------------------------------------------------------")

    def top_up(self):
        student_id = input("Enter Student ID: ")
        student = self.find_student(student_id)
        if not student:
            print("Invalid Student ID.")
            return

        # Display balance details:
        print(f"---------------------------------------------------------")
        print(f"Current Balance: ${float(student['Account']):.2f}")

        # Show Risk Warning:
        if float(student['Account']) <= 2.00:
            print("High Risk of Insufficient funds! Please top up to avoid service interruptions.")
        elif 2.00 < float(student['Account']) <= 6.00:
            print("Moderate Risk of Insufficient funds! Please top up to avoid service interruptions.")
        else:
            print("Low Risk of Insufficient funds.")

        # Prompt for top-up of balance:
        print()
        confirm = input("Do you wish to top-up? (yes/no): ")

        if confirm.lower() != 'yes':
            print("No amount has been topped up to your account.")
            print(f"---------------------------------------------------------")
            return

        # Confirming top-up details
        # Formatted this way so that error message does not show up if the user input does not match the input type
        while True:
            try:
                # Confirming top-up details
                top_up_amount = float(input("How much do you wish to top-up: $"))
                new_top_up_amount = round(top_up_amount, 2)
                break  # Exit the loop if input is valid
            except ValueError:
                print("Invalid input. Please try again.")

        confirm1 = input(f"Is the amount you wish to top up: ${new_top_up_amount:.2f} (yes/no)? ")

        if confirm1.lower() != 'yes':
            print("No amount has been topped up to your account.")
            print(f"---------------------------------------------------------")
            return

        # Playing with time delay:
        messages = [
            f"Topping up... ",
            f"Clink Clink Clank Clank...",
            f"Almost done...",
            f"Top-up Successful!"
        ]
        # Call updating_response function:
        self.updating_response(messages, 1)

        # Show balance detail after top-up
        print(f"---------------------------------------------------------")
        print(f"The amount you have topped up is: ${new_top_up_amount:.2f}")
        student['Account'] = str(float(student['Account']) + new_top_up_amount)
        print(f"Current Balance: ${float(student['Account']):.2f}")
        print(f"---------------------------------------------------------")

    # Program Flow:
    def run(self):
        while True:
            self.display_menu()
            option = input("Enter option: ")
            if option == '1':
                self.rent_locker()
            elif option == '2':
                self.request_move()
            elif option == '3':
                self.return_locker()
            elif option == '4':
                self.enquire_locker_location()
            elif option == '5':
                self.view_usage_report()
            elif option == '6':
                self.top_up()
            elif option == '0':
                messages = [
                    "Exiting Student Program...",
                    "Almost done...",
                    "Returning to main menu..."
                ]
                self.updating_response(messages, 1)
                break
            else:
                print("Feature not implemented yet.")


