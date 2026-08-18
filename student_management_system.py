
STUDENT MANAGEMENT SYSTEM
==========================
A console-based Student Management System built with Python and SQLite.

Features:
- Add / View / Update / Delete student records
- Search students by ID or Name
- Record and update marks/grades per subject
- Auto-calculate percentage and grade
- View all students sorted by percentage
- Data persisted in a local SQLite database (students.db)

import sqlite3
import os

DB_NAME = "students.db"


# ---------------------------------------------------------------------
# DATABASE SETUP
# ---------------------------------------------------------------------
def connect_db():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    """Create the required tables if they do not already exist."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT,
            course TEXT,
            email TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            score REAL NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (student_id)
                ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------------------
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\nPress Enter to continue...")


def calculate_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    else:
        return "F"


def get_valid_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_valid_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid number.")


# ---------------------------------------------------------------------
# CORE STUDENT OPERATIONS
# ---------------------------------------------------------------------
def add_student():
    clear_screen()
    print("=== ADD NEW STUDENT ===\n")

    name = input("Enter student name: ").strip()
    age = get_valid_int("Enter age: ")
    gender = input("Enter gender: ").strip()
    course = input("Enter course/branch: ").strip()
    email = input("Enter email: ").strip()

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO students (name, age, gender, course, email)
        VALUES (?, ?, ?, ?, ?)
    """, (name, age, gender, course, email))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    print(f"\nStudent '{name}' added successfully with ID: {new_id}")

    # Optionally add marks right away
    add_now = input("Add marks for this student now? (y/n): ").strip().lower()
    if add_now == "y":
        add_marks(new_id)

    pause()


def view_all_students():
    clear_screen()
    print("=== ALL STUDENTS ===\n")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY student_id")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No student records found.")
    else:
        print(f"{'ID':<5}{'Name':<20}{'Age':<5}{'Gender':<10}{'Course':<15}{'Email':<25}")
        print("-" * 80)
        for row in rows:
            print(f"{row[0]:<5}{row[1]:<20}{row[2]:<5}{row[3] or '-':<10}{row[4] or '-':<15}{row[5] or '-':<25}")

    pause()


def search_student():
    clear_screen()
    print("=== SEARCH STUDENT ===\n")
    print("1. Search by ID")
    print("2. Search by Name")
    choice = input("Choose an option: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    if choice == "1":
        sid = get_valid_int("Enter student ID: ")
        cursor.execute("SELECT * FROM students WHERE student_id = ?", (sid,))
    elif choice == "2":
        name = input("Enter name (or part of it): ").strip()
        cursor.execute("SELECT * FROM students WHERE name LIKE ?", (f"%{name}%",))
    else:
        print("Invalid choice.")
        pause()
        conn.close()
        return

    results = cursor.fetchall()
    conn.close()

    if not results:
        print("\nNo matching student found.")
    else:
        for row in results:
            print("\n--- Student Found ---")
            print(f"ID       : {row[0]}")
            print(f"Name     : {row[1]}")
            print(f"Age      : {row[2]}")
            print(f"Gender   : {row[3]}")
            print(f"Course   : {row[4]}")
            print(f"Email    : {row[5]}")
            show_student_marks(row[0])

    pause()


def update_student():
    clear_screen()
    print("=== UPDATE STUDENT ===\n")
    sid = get_valid_int("Enter student ID to update: ")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (sid,))
    student = cursor.fetchone()

    if not student:
        print("Student not found.")
        conn.close()
        pause()
        return

    print("Leave field blank to keep the current value.\n")
    name = input(f"Name [{student[1]}]: ").strip() or student[1]
    age_input = input(f"Age [{student[2]}]: ").strip()
    age = int(age_input) if age_input else student[2]
    gender = input(f"Gender [{student[3]}]: ").strip() or student[3]
    course = input(f"Course [{student[4]}]: ").strip() or student[4]
    email = input(f"Email [{student[5]}]: ").strip() or student[5]

    cursor.execute("""
        UPDATE students
        SET name = ?, age = ?, gender = ?, course = ?, email = ?
        WHERE student_id = ?
    """, (name, age, gender, course, email, sid))
    conn.commit()
    conn.close()

    print("\nStudent record updated successfully.")
    pause()


def delete_student():
    clear_screen()
    print("=== DELETE STUDENT ===\n")
    sid = get_valid_int("Enter student ID to delete: ")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM students WHERE student_id = ?", (sid,))
    student = cursor.fetchone()

    if not student:
        print("Student not found.")
        conn.close()
        pause()
        return

    confirm = input(f"Are you sure you want to delete '{student[0]}'? (y/n): ").strip().lower()
    if confirm == "y":
        cursor.execute("DELETE FROM marks WHERE student_id = ?", (sid,))
        cursor.execute("DELETE FROM students WHERE student_id = ?", (sid,))
        conn.commit()
        print("Student deleted successfully.")
    else:
        print("Deletion cancelled.")

    conn.close()
    pause()


# ---------------------------------------------------------------------
# MARKS / GRADES OPERATIONS
# ---------------------------------------------------------------------
def add_marks(student_id=None):
    clear_screen()
    print("=== ADD MARKS ===\n")

    if student_id is None:
        student_id = get_valid_int("Enter student ID: ")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()

    if not student:
        print("Student not found.")
        conn.close()
        pause()
        return

    print(f"Adding marks for: {student[0]}")
    num_subjects = get_valid_int("How many subjects to add? ")

    for _ in range(num_subjects):
        subject = input("Subject name: ").strip()
        score = get_valid_float(f"Score for {subject} (out of 100): ")
        cursor.execute("""
            INSERT INTO marks (student_id, subject, score)
            VALUES (?, ?, ?)
        """, (student_id, subject, score))

    conn.commit()
    conn.close()

    print("\nMarks added successfully.")
    pause()


def show_student_marks(student_id):
    """Helper to display marks + percentage + grade for a given student."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT subject, score FROM marks WHERE student_id = ?", (student_id,))
    marks = cursor.fetchall()
    conn.close()

    if not marks:
        print("No marks recorded yet.")
        return

    print("\n--- Marks ---")
    total = 0
    for subject, score in marks:
        print(f"{subject:<20}: {score}")
        total += score

    percentage = total / len(marks)
    grade = calculate_grade(percentage)
    print(f"\nPercentage: {percentage:.2f}%")
    print(f"Grade     : {grade}")


def view_student_report():
    clear_screen()
    print("=== STUDENT REPORT CARD ===\n")
    sid = get_valid_int("Enter student ID: ")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (sid,))
    student = cursor.fetchone()
    conn.close()

    if not student:
        print("Student not found.")
    else:
        print(f"Name  : {student[1]}")
        print(f"Course: {student[4]}")
        show_student_marks(sid)

    pause()


def rank_students():
    """View all students sorted by average percentage, highest first."""
    clear_screen()
    print("=== STUDENT RANKINGS (by percentage) ===\n")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, name FROM students")
    students = cursor.fetchall()

    ranking = []
    for sid, name in students:
        cursor.execute("SELECT score FROM marks WHERE student_id = ?", (sid,))
        scores = [row[0] for row in cursor.fetchall()]
        if scores:
            percentage = sum(scores) / len(scores)
            ranking.append((name, percentage, calculate_grade(percentage)))

    conn.close()

    ranking.sort(key=lambda x: x[1], reverse=True)

    if not ranking:
        print("No marks data available yet.")
    else:
        print(f"{'Rank':<6}{'Name':<20}{'Percentage':<12}{'Grade':<6}")
        print("-" * 44)
        for i, (name, pct, grade) in enumerate(ranking, start=1):
            print(f"{i:<6}{name:<20}{pct:<12.2f}{grade:<6}")

    pause()


# ---------------------------------------------------------------------
# MAIN MENU
# ---------------------------------------------------------------------
def main_menu():
    create_tables()

    while True:
        clear_screen()
        print("=" * 40)
        print("     STUDENT MANAGEMENT SYSTEM")
        print("=" * 40)
        print("1. Add Student")
        print("2. View All Students")
        print("3. Search Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Add Marks")
        print("7. View Student Report Card")
        print("8. View Rankings")
        print("9. Exit")
        print("=" * 40)

        choice = input("Enter your choice (1-9): ").strip()

        if choice == "1":
            add_student()
        elif choice == "2":
            view_all_students()
        elif choice == "3":
            search_student()
        elif choice == "4":
            update_student()
        elif choice == "5":
            delete_student()
        elif choice == "6":
            add_marks()
        elif choice == "7":
            view_student_report()
        elif choice == "8":
            rank_students()
        elif choice == "9":
            print("\nExiting Student Management System. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
            pause()


if __name__ == "__main__":
    main_menu()
