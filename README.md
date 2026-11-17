# Smart Exam Hall: Anti-Cheating Seat Allocator

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-6B8E7F)
![MySQL](https://img.shields.io/badge/Database-MySQL-4479A1?logo=mysql&logoColor=white)

A desktop application that seats students in exam halls automatically. It makes sure that students who could copy from each other (same subject, or same branch) are not placed next to one another.

Built with **Python (Tkinter)** for the interface and **MySQL** for storage. The whole project is two files: `exam_hall_app.py` and `setup.sql`.

---

## Why this project

- Seating charts made by hand take hours and are easy to get wrong.
- Students of the same subject often end up side by side by mistake.
- Seating in reg-no order is predictable, which makes copying easy to plan.
- Any change in students or halls means redoing the whole chart.

This app generates a valid seating plan in seconds, and re-checks its own result.

## Features

- **Student management**: add, update, delete and search students (reg no, name, branch, subject code)
- **Hall setup**: define each hall as rows × columns; capacity is calculated automatically
- **One-click allocation**: builds a conflict-free seating plan for all students and halls
- **Seating chart**: a grid for each hall, one colour per subject, grey for empty seats
- **Find my seat**: enter a reg no to get the hall, row and column
- **CSV export**: save the full allocation for printing or the notice board
- **Self-check**: `validate_allocation()` re-checks every adjacent pair and shows the violation count

## Screenshots

> Add your screenshots to a `docs/` folder and update the paths below.

| Seating Chart | Students | Allocate Seats |
|---|---|---|
| ![Seating chart](docs/seating-chart.png) | ![Students tab](docs/students.png) | ![Allocate tab](docs/allocate.png) |

## How the allocation works

1. **Load data**: read all students and halls from MySQL.
2. **Check capacity**: if seats are fewer than students, show the shortage and stop.
3. **Shuffle**: randomise the student order so there is no fixed pattern.
4. **Fill seats**: go hall by hall, row by row, and pick a student who does not clash with the left and front neighbours.
5. **Retry, keep best**: try up to 200 random orderings and keep the one with the fewest problems.
6. **Validate and save**: re-check every pair, then save to the `allocations` table in one transaction.

If no student fits a seat without breaking the same-subject rule, the seat is left empty instead.

## How conflicts are identified

Every seat is compared with the seats to its **left, right, front and back**.

| Rule | Type | Behaviour |
|---|---|---|
| Same subject code next to each other | **Hard** | Never allowed. The seat stays empty if needed. |
| Same branch next to each other | **Soft** | Avoided first, allowed only if there is no other option. |

Example of a 3 × 5 hall (letters are subjects), where no two neighbouring seats share a subject:

```
A B C A B
C A B C A
B C A B C
```

## Tech stack

| Part | Used for |
|---|---|
| Python 3 | Application logic and the allocation algorithm |
| Tkinter / ttk | Desktop interface: tabs, tables, and a canvas for the seating chart |
| MySQL + MySQL Workbench | Database for students, halls and allocations |
| mysql-connector-python | Connecting the app to MySQL (all queries use `%s` placeholders) |

## Project structure

```
.
├── exam_hall_app.py   # Tkinter application and allocation algorithm
├── setup.sql          # Creates exam_hall_db, tables and sample data
├── docs/              # Screenshots (optional)
└── README.md
```

## Database schema

| Table | Columns |
|---|---|
| `students` | `id`, `reg_no` (unique), `name`, `branch`, `subject_code` |
| `halls` | `id`, `hall_name` (unique), `total_rows`, `total_cols` |
| `allocations` | `id`, `student_id`, `hall_id`, `row_no`, `col_no` |

`allocations` uses foreign keys with `ON DELETE CASCADE`, a unique `(hall_id, row_no, col_no)` so a seat holds one student, and a unique `student_id` so a student has one seat.

## Getting started

### Prerequisites

- Python 3.8 or newer (Tkinter ships with the standard Python installer)
- MySQL Server and MySQL Workbench

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/<your-repo>.git
   cd <your-repo>
   ```

2. **Install the MySQL connector**
   ```bash
   pip install mysql-connector-python
   ```

3. **Create the database**
   - Open MySQL Workbench and double-click your connection to open a SQL editor tab.
   - Use *File → Open SQL Script* and choose `setup.sql`.
   - Click the lightning bolt (or press `Ctrl+Shift+Enter`) to run it. This creates `exam_hall_db`, the tables and some sample data.

4. **Set your database password**

   Open `exam_hall_app.py` and edit `DB_CONFIG` near the top:
   ```python
   DB_CONFIG = {
       "host": "localhost",
       "user": "root",
       "password": "YOUR_PASSWORD",
       "database": "exam_hall_db",
   }
   ```

5. **Run the app**
   ```bash
   python exam_hall_app.py
   ```

## Usage

1. **Students** tab: add or import your students (or use the sample data).
2. **Halls** tab: add the halls with their rows and columns.
3. **Allocate Seats** tab: click *Generate Allocation* and read the summary (students seated, halls used, violations).
4. **Seating Chart** tab: pick a hall to see the colour-coded grid.
5. **Find My Seat** tab: look up a student by reg no.
6. Use *Export to CSV* to save the final plan.

## Suggested test cases

| Test | Input | Expected result |
|---|---|---|
| Normal allocation | 40 sample students, 3 halls | All seated, 0 same-subject violations |
| Not enough seats | More students than total capacity | Error shows how many seats are short |
| Only one subject | All students share one subject code | Rule is never broken; extra students reported as unseated |
| Duplicate reg no | Add a student with an existing reg no | Rejected with a warning |
| Generate twice | Click *Generate Allocation* two times | Old allocation replaced, new one is still valid |
| Find my seat | A valid and an invalid reg no | Hall, row and column shown / not-found message |

## Troubleshooting

| Problem | Fix |
|---|---|
| Lightning bolt is greyed out in Workbench | Open the script from a SQL editor tab that is connected to your server, not straight from the File menu |
| `Access denied for user 'root'` | The password in `DB_CONFIG` is wrong |
| `Unknown database 'exam_hall_db'` | `setup.sql` has not been run yet |
| `No module named 'mysql'` | Run `pip install mysql-connector-python` |
| Cannot connect to the server | Start the MySQL service (`MySQL80` in Windows Services) |

## Known limitations

- The allocation is a randomised search, not an exact solver, so very tight halls may leave some seats empty.
- One exam session at a time.
- No login or user roles.

## Future scope

- Multiple exam sessions with clash checks
- Invigilator allocation for each hall
- PDF seating plans and hall tickets
- Web version where students log in to see their seat
- Smarter search (backtracking or graph colouring) for tight cases

## Author

**Nimesh Joshi**
SRM Institute of Science and Technology, Kattankulathur

## License

Add a license of your choice (for example MIT) before publishing.
