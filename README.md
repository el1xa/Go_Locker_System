# Go Locker — Campus Locker Rental System
A console-based locker rental management system simulating a smart campus locker network. Built as a group project for a university Python module, modelled after NTU's campus infrastructure.

## Overview
Go Locker supports two separate operation modes — Admin and Student — each with their own menu, permissions, and functionality. All data is persisted in a JSON file, simulating a lightweight database.

## Features

### Student Mode
- **Rent a locker** — Automatically assigns the next available locker; deducts rental fee from account balance; enforces a maximum of 2 active rentals per student
- **Request move** — Relocates a locker to a different campus station or back to central store; checks slot availability and deducts moving fee
- **Return locker** — Returns locker to central store; generates a charge summary (rental + move fees)
- **Enquire locker location** — View current location and rental details for active rentals
- **View usage report** — Full rental history including timestamps, move operations, and total charges
- **Check balance / Top-up** — View current account balance with risk warnings; top up in custom amounts

### Admin Mode
- **Setup station** — Create new locker stations with custom station code (regex-validated), name, rows, and columns; auto-generates all slots
- **Create locker** — Add new lockers to the system with location and status
- **Update locker** — Modify locker location or status; handles suspension and rental termination
- **View station report** — Slot utilization report showing which lockers are assigned to which students
- **Track locker usage** — Filter a locker's full move history by date range
- **Change rental/moving fees** — Update system-wide fees

## How to Run

**Requirements:** Python 3.7 or above — no external libraries needed

```bash
# Clone the repository
git clone https://github.com/yourusername/go-locker.git
cd go-locker

# Run the program
python main.py
```

## Project Structure

```
go-locker/
├── main.py          # Entry point — main menu, mode selection
├── studentMode.py   # Student-facing rental operations
├── adminMode.py     # Admin-facing station and locker management
└── appendixA.json   # JSON data store (stations, lockers, students)
```

## Technical Highlights

- **Multi-role architecture** — Clean separation between admin and student systems across multiple modules
- **JSON data persistence** — All changes written back to `appendixA.json` in real time, simulating database behaviour
- **Regex input validation** — Station codes validated against `NTU-XYY-DD` format using `re` module
- **Move history logging** — Every rental, move, and return recorded with timestamp and operation type
- **Fee calculation engine** — Automatically tallies rental and move charges per rental session
- **Edge case handling** — Covers insufficient balance, duplicate rentals, invalid IDs, closed stations, full slots, and same-location moves
- **Animated CLI feedback** — Uses `sys.stdout` for real-time status updates during locker move operations

## Sample Interaction

```
++++ Welcome to GO 'MOBILE' Locker ++++
A. Admin Mode
B. Student Mode
0. Exit

Enter your choice: B

++++ Go Locker – Operations ++++
1. Rent a locker
2. Request move
3. Return locker
4. Enquire locker location
5. View usage report
6. Check Balance/Top-Up
0. Exit
```

## Notes

- Developed as a group project as a group of 5
- Data is pre-loaded with sample stations across NTU campus locations (Admin Building, North Spine, The Arc, The Hive, SSC)
- No external dependencies — uses only Python standard library (`json`, `re`, `datetime`, `sys`, `time`)
