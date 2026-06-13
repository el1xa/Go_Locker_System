import json
import time
import sys
import re
from datetime import datetime


class AdminSystem:
    def __init__(self):
        # Load data from JSON file
        with open('appendixA.json', 'r') as file:
            self.data = json.load(file)

    def display_menu(self):
        print("\n^^^^ Go locker - Admin ^^^^")
        print("1. Setup station")
        print("2. Create locker")
        print("3. Update locker")
        print("4. View station report")
        print("5. Track locker usage")
        print("6. Change Rental/Moving Fees of Lockers")
        print("0. Exit")

    def validate_station_code_input(self,input_str): #create_station --> station Code
        # Validate the format of user's input:
        pattern = r"^NTU-[A-Z]\d{2}-\d{2}$"  # Matches 'NTU-XYY-DD' format

        # Check if input matches the pattern
        if re.match(pattern, input_str):
            # Extract the last two digits (DD part) and check if it's within 00-99
            dd_value = int(input_str[-2:])  # Extract last two digits as an integer
            if 0 <= dd_value <= 99:
                return True

    def append_slots_to_station(self, station_code, station_name, row, columns):

        # Find the station in the data
        station = None
        for s in self.data['stations']:
            if s['stationCode'] == station_code:
                station = s
                break

        # If station is not found, print an error
        if station is None:
            print(f"Station {station_code} not found in the data.")
            return

        # Create the new slots
        new_slots = []
        for r in range(1, row + 1):
            for c in range(1, columns + 1):
                slot_id = f"{station_code} ({r:01d}-{c:02d})"
                new_slots.append({
                    "slotID": slot_id,
                    "statusID": "Available"
                })

        # Append the new slots to the station's slots
        if 'slots' not in station:
            station['slots'] = []  # Create the slots list if it doesn't exist
        station['slots'].extend(new_slots)

        # Save the updated data back to the JSON file
        with open('appendixA.json', 'w') as file:
            json.dump(self.data, file, indent=4)

        print(f"---------------------------------------------------------"
              f"\nSuccessful Creation of Station:"
              f"\nStation Code: {station_code} \tStation Name: {station_name} "
              f"\nRows: {row} \t Columns: {columns} \tNumber of slots: {len(new_slots)}"
              f"\n---------------------------------------------------------")

    # for delay in response (move)
    def updating_response(self, messages, delay=1):
        for message in messages:
            # It clears the line and prints the new message
            sys.stdout.write('\r' + ' ' * 80)
            sys.stdout.write('\r' + message)
            sys.stdout.flush()  # Ensures that the character is printed immediately
            time.sleep(delay)  # Wait for the specified delay
        print()  # Moves to the next line after the final message

#Code for different functions starts here:
    # Function to create a new station entry
    def create_station(self):
        #Prompt for user input for Station Code:
        print("\n-----Creating station-----")
        station_code = input("Enter Station Code: ")

        #Validate the user input (Station Code):
        if not self.validate_station_code_input(station_code): #If the input is invalid
            print("Invalid Input, please try again.")
            return

        #Check if the station code already exists: (if exists, return)
        for station in self.data['stations']:
            if station_code == station['stationCode']:
                print("Station Code already exists.")
                return

        #Validate the user input (Station Name):
        station_name = input("Enter Station Name: ")

        #Check if the station name already exists: (if exists, return)
        for station in self.data['stations']:
            if station_name == station['stationName']:
                print("Station name already exists.")
                return

        #(Rows and Columns) Formatted it this way so that error message does not show up even if type(user_input) is not integer
        while True:
            try:
                rows = int(input("Enter Rows: "))
                columns = int(input("Enter Columns: "))
                break #Exit the loop if the input is valid
            except ValueError:
                print("Invalid input")

        #Status:
        while True:
            status = input("Enter Status (Open/Closed): ").lower()
            if status == "open" or status.lower() == "closed":
                status = status.capitalize()
                break
            else:
                print("Invalid input")

        #Creating the new station data as a dictionary
        new_station = {
            "stationCode": station_code,
            "stationName": station_name,
            "rows": rows,
            "columns": columns,
            "status": status,
            "slots": []  # Initialize empty slots for new station
        }
        # Adding new station to the list
        self.data['stations'].append(new_station)

        #Appending slots:
        self.append_slots_to_station(station_code, station_name, rows, columns)

        # Save the updated data back to the JSON file
        with open('appendixA.json', 'w') as file:
            json.dump(self.data, file, indent=4)

    # Function to create a new locker entry
    def create_locker(self):
        # Find the next available Locker ID
        if self.data['lockers']:
            max_id = max(int(locker["lockerID"]) for locker in self.data['lockers'])
            next_id = str(max_id + 1)
        else:
            next_id = "10001"

        # Prompt for user input to key in location of locker
        print("\n----Creating locker----")
        location = input("Enter Location (Central store, In transit, or Station Code): ")

        # If user input is anything other than "Central store", "In transit" or valid station code, then default to "Central store"
        station_codes = [station['stationCode'] for station in self.data['stations']]
        if location not in ["Central store", "In transit"] + station_codes:
            location = "Central store"  # Default to "Central store" if the location is invalid

        #Row/Column: If the locker is in a valid location or station, the user will be prompted to input a value. Else, default row to 0
        if location not in station_codes:
            rows = 0
            columns = 0
        else:
            while True:
                try:
                    rows = int(input("Enter Rows: "))
                    columns = int(input("Enter Columns: "))
                    break  # Exit the loop if the input is valid
                except ValueError:
                    print("Invalid input")

        #Status: (default to "Available")
        status = input("Enter Status (Occupied, Available, Suspended): ").lower()
        if status not in ["occupied", "available", "suspended"]:
            status = "Available"
        else:
            status = status.capitalize()

        #If the locker is occupied, the prompt for rental ID:
        rental_id = input("Enter Rental ID: ") if status == "Occupied" else ""
        #Validate if the rental ID that user input:
        valid_student_ID = [student['studentID'] for student in self.data['students']]
        if rental_id and rental_id not in valid_student_ID:
            print("Invalid Rental ID")
            return

        # Creating the new locker data as a dictionary
        new_locker = {
            "lockerID": next_id,
            "previousLocation": None,
            "location": location,
            "row": rows,
            "columns": columns,
            "status": status,
            "rentalID": rental_id,
            "startDate": "",
            "endDate": "",
            "rentalIDCounter": None
        }
        # Adding new station to the list
        self.data['lockers'].append(new_locker)

        #Displaying the details of the locker being created:
        print(f"---------------------------------------------------------"
              f"\nSuccessful Creation of Locker:"
              f"\nLocker ID: {new_locker['lockerID']} \tLocation: {new_locker['location']}"
              f"\nRows: {new_locker['row']} Columns: {new_locker['columns']} \tStatus: {new_locker['status']}"
              f"\n---------------------------------------------------------")

        # Save the entire JSON structure
        with open('appendixA.json', 'w') as file:
            json.dump(self.data, file, indent=4)

    # Function to update a locker entry
    def update_locker(self):
        #Prompt for Admin to enter locker ID to update
        print()
        print("----Updating locker----")

        # Searching if locker ID exists
        locker_id = input("Enter the Locker ID to update: ")
        locker = next((l for l in self.data['lockers'] if l["lockerID"] == locker_id), None)

        # If locker ID is not found, show error message
        if locker is None:
            print("Error: Locker ID not found.")
            return

        #Initialise a flag to track if the locker with the specified ID is found
        locker_found = False

        # Iterate over each locker in the data
        for l in self.data['lockers']:
            if l['lockerID'] == locker_id:
                locker_found = True  # Set flag to True since we found the matching locker

                # Find the student with the rentalID (if the locker is occupied)
                if l['status'] == "Occupied":
                    # Find the student associated with the rental ID
                    student = next((s for s in self.data['students'] if s['studentID'] == l['rentalID']), None)

                    # Print locker details if student found
                    if student:
                        print("\nCurrent Locker Details:")
                        print(f"---------------------------------------------------------")
                        print(f"Locker ID: {l['lockerID']} \tStatus: {l['status']}")
                        print(f"Student ID: {l['rentalID']} \tStudent Name: {student['studentName']}")
                        print(f"Start Date: {l['startDate']} \tLocation: {l['location']}")
                        print(f"---------------------------------------------------------")
                    else:
                        pass

                else:
                    # Print details for non-occupied lockers
                    print("\nCurrent Locker Details:")
                    print(f"---------------------------------------------------------")
                    print(f"Locker ID: {l['lockerID']} \tStatus: {l['status']}")
                    print(f"Location: {l['location']} \tRows: {l['row']} \tColumns: {l['columns']}")
                    print(f"---------------------------------------------------------")

                # Exit the loop once we find and print the details for the matching locker
                break

        # Prompt for user to update locker details (Location and status)
        new_location = input("Enter new Location (leave blank to keep current): ")

        #Updating value in new_location if ""
        if new_location == "":
            new_location = l['location']

        #Checking if location for locker exists: (If None, return)
        location = next((s for s in self.data['stations'] if s['stationCode'] == new_location or s['stationCode'] == new_location[:-7]), None)
        if location is None and new_location != "Central store":
            print("Error: Location not found.")
            return
        else:
            locker['location'] = new_location

        #Prompt for User to update Status:
        print("If you do not wish to change the current status of the locker, leave blank.")
        new_status = input("Enter new Status (Available, Suspended): ").lower()

        #Rejecting invalid input:
        if new_status not in ["available", "suspended", ""]:
            print("Invalid input.")
            return
        else:
            new_status = new_status.capitalize()

        #If the current status is the same as user input:
        if new_status == l['status']:
            print(f"Current status is same as User input: {l['status']}")
            return

        #If you want to suspend the locker: (Condition: status must be available)
        if new_status == "Suspended" and l["status"] != "Available":
            print("Error: Status can only be updated to 'Suspended' when the current status is 'Available'.")
            return
        else:
            pass

        #Changing locker to Occupied when it is Available:
        locker_id_to_update = locker_id
        for l in self.data['lockers']:
            if l['rentalID'] == locker_id_to_update:
                if new_status == "Available" and l["status"] == "Occupied":
                    if 'moveHistory' in l:
                        for move in l['moveHistory']:
                            if l["rentalIDCounter"] == move['rentalIDCounter1'] and l['rentalID'] == move['userID']:
                                move["operation"] = "Suspended"
                    l["previousLocation"] = None
                    l["location"] = new_location
                    l["status"] = "Available"
                    l["rentalID"] = ""
                    l['startDate'] = ""
                    l['endDate'] = ""
                    l['rentalIDCounter'] = None
                    print("Rental record terminated.")
                    print(f"{l['status']}")
                    break
            else:
                pass

        if new_status != "":
            locker['status'] = new_status
            print(f"Locker's status has been updated to {l['status']} ")
        else:
            print(f"Locker's status remains unchanged: {l['status']}")

        # Save the updated data back to the JSON file
        with open('appendixA.json', 'w') as file:
            json.dump(self.data, file, indent=4)

    # Function to check a station report
    def view_station_utilization_report(self):
        stations = self.data.get("stations", [])  # Extract stations list
        lockers = {locker['lockerID']: locker for locker in self.data.get('lockers', [])}  # Convert lockers list to dictionary
        students = {student['studentID']: student for student in
                    self.data.get('students', [])}  # Convert students list to dictionary

        # Step 1: Get station code input from user
        print("\n----View Station Report----")
        station_code = input("Enter the station code to view utilization report: ")

        # Step 2: Search for the station by code
        station = None
        for s in stations:
            if s.get('stationCode') == station_code:
                station = s
                break

        # Step 2: If station is not found, display error and return
        if not station:
            print("Error: No station found with the provided code.")
            return

        # Step 3: Display station details
        print(f"\nStation Code: {station['stationCode']}")
        print(f"Station Name: {station['stationName']}")
        print(f"Rows: {station['rows']}")
        print(f"Columns: {station['columns']}")
        print(f"Status: {station['status']}")
        print("\nSlot Utilization Report:")

        # Formatting the report if rental_id matches:
        # (UpperDivision)
        border = ""
        filler = " "
        rowStr = "" + border
        rowStr += "".center(20, filler) + border
        rowStr += "".center(16, filler) + border
        rowStr += "".center(18, filler) + border

        # (Text 1st Row)
        rowStr += "\n"
        filler = " "
        rowStr += "" + border
        rowStr += "Slots".center(20, filler) + border
        rowStr += "Locker ID".center(16, filler) + border
        rowStr += "Student Name".center(18, filler) + border
        print(rowStr)

        # Step 4: Display each slot's utilization status
        print("-" * 55)

        # Iterate through the slots in the station
        for slot in station.get('slots', []):
            slot_id = slot.get('slotID')

            # Find the locker assigned to this slot based on the `location`
            locker = next((locker for locker in self.data['lockers'] if locker['location'] == slot_id), None)

            if locker:
                if locker['status'] == 'Occupied':
                    rental_id = locker['rentalID']
                    student = students.get(rental_id)
                    student_name = student['studentName'] if student else "Unknown"
                    locker_id = locker['lockerID']
                else:
                    locker_id = "Empty"
                    student_name = "-"
            else:
                locker_id = "Empty"
                student_name = "-"

            print(f"{slot_id:<10} | {locker_id:<10} | {student_name}")

        print("-" * 50)

    # Function to track usage report
    def track_usage_report(self):

        lockers = {locker['lockerID']: locker for locker in self.data.get('lockers', [])}

        print("\n----Track locker Usage----")
        locker_id = input("Enter the Locker ID to track usage: ")

        # Check if the locker_id exists in the lockers dictionary
        locker = lockers.get(locker_id)

        if not locker:
            print("Error: Locker ID does not exist in appendix.")
            return

        # Loop to handle date inputs
        while True:
            try:
                # Get the start and end dates from the user
                date_from = datetime.strptime(input("Enter start date (e.g., 14-Aug-2024): "), "%d-%b-%Y")
                date_to = datetime.strptime(input("Enter end date (e.g., 15-Oct-2024): "), "%d-%b-%Y")

                #Check if the end date is earlier than the start date:
                if date_to < date_from:
                    print("End date cannot be earlier than start date. Please try again.")
                else:
                    break #Break out of the loop if both dates are valid and in correct order

            except ValueError:
                # Print error message and ask for input again if date format is incorrect
                print("Invalid Input. Please enter date in the format: dd-Mmm-yyyy (e.g., 14-Aug-2024)")

        # Display locker information
        print(f"\nLocker ID: {locker['lockerID']}")
        print(f"Location: {locker['location']}")
        print(f"Status: {locker['status']}")

        if locker['status'] == 'Occupied' and locker.get('rentalID'):
            students = {student['studentID']: student for student in self.data.get('students', [])}
            student = students.get(locker['rentalID'])

            if student:
                print(f"Student ID: {student['studentID']}")
                print(f"Student Name: {student['studentName']}")
                print(f"Rental Start Date: {locker.get('startDate')}")

        # Print header for operations
        # (UpperDivision)
        border = ""
        filler = " "
        rowStr = "" + border
        rowStr += "".center(13, filler) + border
        rowStr += "".center(9, filler) + border
        rowStr += "".center(28, filler) + border
        rowStr += "".center(12, filler) + border

        # (Text 1st Row)
        rowStr += "\n"
        filler = " "
        rowStr += "" + border
        rowStr += "Date".ljust(13, filler) + border
        rowStr += "Time".ljust(9, filler) + border
        rowStr += "Operation".center(28, filler) + border
        rowStr += "Student ID".ljust(12, filler) + border

        # (Bottom division)
        rowStr += "\n"
        filler = "-"
        rowStr += "" + border
        rowStr += "".ljust(13, filler) + border
        rowStr += "".ljust(9, filler) + border
        rowStr += "".ljust(28, filler) + border
        rowStr += "".ljust(12, filler) + border

        rowStr += ""
        filler = " "
        rowStr += "" + border
        print(rowStr)

        # Display filtered move history
        for move in locker.get("moveHistory", []):
            move_date = datetime.strptime(move['timestamp'], "%d-%b-%Y")
            if date_from <= move_date <= date_to:
                timestamp = move['timestamp']
                time = move.get('timestampTime', "00:00")  # Default to "00:00" if not available
                operation = move.get('operation', "Unknown")
                student_id = move.get('userID', "-")

                # Print formatted row with specific widths for each column
                # Construct the row string for output
                rowStr = "" + border  # Reset rowStr for new entry
                rowStr += "" + border
                rowStr += f"{timestamp}".ljust(13, filler) + border
                rowStr += f"{time}".ljust(9, filler) + border
                rowStr += f"{operation}".ljust(28, filler) + border
                rowStr += f"{student_id}".ljust(12, filler) + border

                print(rowStr)  # Print the constructed row string

        print("-------------------------------------------------------------")

    def changing_fees(self):
        print("\n----Change Rental/Moving fees of Lockers----")

        while True:
            try:
                #Prompt for user to key in new moving fee:
                print("If you do not wish to change rental fee, press 'enter' key on keyboard.")
                new_rental_fee_input = input("Enter new rental fee of lockers: ")

                #If user presses 'enter' key (empty string), do not change the fee
                if new_rental_fee_input == "":
                    print(f"Rental fee remains unchanged at ${self.data['rentalFee']:.2f}")
                    break

                # Convert the input to float if it's not empty
                new_rental_fee = float(new_rental_fee_input)

                # Round it to two decimal places
                new_rental_fee = round(new_rental_fee, 2)

                #Check if the value is valid (non-negative)
                if new_rental_fee >= 0:
                    self.data['rentalFee'] = new_rental_fee
                    print(f"Rental fee updated to: ${self.data['rentalFee']:.2f}")
                    break
                else:
                    print("Rental fee must be a positive number. Please try again.")

            except ValueError:
                print("Invalid input. Please enter a valid number.")

        while True:
            try:
                #Prompt for user to key in new moving fee:
                print("If you do not wish to change moving fee, press 'enter' key on keyboard.")
                new_moving_fee_input = input("Enter new moving fee of lockers: ")

                #If user presses 'enter' key (empty string), do not change the fee
                if new_moving_fee_input == "":
                    print(f"Moving fee remains unchanged at ${self.data['movingFee']:.2f}")
                    break

                # Convert the input to float if it's not empty
                new_moving_fee = float(new_moving_fee_input)

                # Round it to two decimal places
                new_moving_fee = round(new_moving_fee, 2)

                #Check if the value is valid (non-negative)
                if new_moving_fee >= 0:
                    self.data['movingFee'] = new_moving_fee
                    print(f"Moving fee updated to: ${new_moving_fee:.2f}")
                    break
                else:
                    print("Moving fee must be a positive number. Please try again.")

            except ValueError:
                print("Invalid input. Please enter a valid number.")

    # Program Flow:
    def run(self):
        while True:
            self.display_menu()
            option = input("Enter option: ")
            if option == '1':
                self.create_station()
            elif option == '2':
                self.create_locker()
            elif option == '3':
                self.update_locker()
            elif option == '4':
                self.view_station_utilization_report()
            elif option == '5':
                self.track_usage_report()
            elif option == '6':
                self.changing_fees()
            elif option == '0':
                messages = [
                    "Exiting Admin Program...",
                    "Almost done...",
                    "Returning to main menu..."
                ]
                self.updating_response(messages, 1)
                break
            else:
                print("Feature not implemented yet.")