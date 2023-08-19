import tkinter as tk
from tkinter import ttk
import mysql.connector
import tkinter.simpledialog
from tkinter.scrolledtext import ScrolledText
import tkinter.messagebox

"""
CREATE DATABASE student_information_system;

USE student_information_system;

CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(10) NOT NULL,
    course VARCHAR(100) NOT NULL,
    college VARCHAR(100) NOT NULL,
    INDEX idx_course_code (course_code)  -- Add an index on the course_code column
);

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(15) NOT NULL,
    name VARCHAR(225) NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    year_level INT NOT NULL,
    course_code VARCHAR(10) NOT NULL,
    FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE CASCADE
);
"""

# Connect to the MySQL database
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "^eight8finity^",
    "database": "student_information_system"
}

def execute_query(query, params=None):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Fetch the results if the query is a SELECT query
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
        else:
            result = None

        conn.commit()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return result
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# CRUDL operations for Students
def create_student(student_data):
    query = "INSERT INTO students (student_id, name, gender, year_level, course_code) VALUES (%s, %s, %s, %s, %s)"
    execute_query(query, student_data)
    refresh_students()  # Call the refresh function to update the UI

def read_students():
    query = "SELECT * FROM students"
    return execute_query(query)

def update_student(student_data):
    print("Updating student:", student_data)
    query = "UPDATE students SET name=%s, gender=%s, year_level=%s, course_code=%s WHERE id=%s"
    execute_query(query, student_data)
    refresh_students()

def delete_student(student_id):
    query = "DELETE FROM students WHERE student_id=%s"
    execute_query(query, (student_id,))
    refresh_students()  # Call the refresh function to update the UI

def update_student_course(student_id, new_course_code):
    update_query = "UPDATE students SET course_code=%s WHERE student_id=%s"
    execute_query(update_query, (new_course_code, student_id))

def student_id_exists(student_id):
    query = "SELECT COUNT(*) FROM students WHERE student_id = %s"
    result = execute_query(query, (student_id,))
    return result[0][0] > 0

# CRUDL operations for Courses
def create_course(course_data):
    query = "INSERT INTO courses (course_code, course, college) VALUES (%s, %s, %s)"
    execute_query(query, course_data)
    refresh_courses()  # Call the refresh function to update the UI
    refresh_students()  # Update the student frame dropdown with the latest course codes

def read_courses():
    query = "SELECT * FROM courses"
    return execute_query(query)

def update_course(course_data):
    query = "UPDATE courses SET course=%s, college=%s WHERE id=%s"
    execute_query(query, course_data)
    refresh_courses()  # Call the refresh function to update the UI
    refresh_students()  # Update the student frame dropdown with the latest course codes

def delete_course(course_code):
    # Set course code of enrolled students to a value indicating not enrolled
    update_query = "UPDATE students SET course_code='N/A' WHERE course_code=%s"
    execute_query(update_query, (course_code,))
    
    # Delete the course from the courses table
    query = "DELETE FROM courses WHERE course_code=%s"
    execute_query(query, (course_code,))
    
    refresh_courses()  # Call the refresh function to update the UI
    refresh_students()  # Update the student frame dropdown with the latest course codes

def search_students(query):
    search_query = f"SELECT * FROM students WHERE name LIKE '%{query}%' OR student_id LIKE '%{query}%'"
    return execute_query(search_query)

def search_courses(query):
    search_query = f"SELECT * FROM courses WHERE course_code LIKE '%{query}%' OR course LIKE '%{query}%'"
    return execute_query(search_query)

def course_code_exists(course_code):
    query = "SELECT COUNT(*) FROM courses WHERE course_code = %s"
    result = execute_query(query, (course_code,))
    return result[0][0] > 0

# GUI functions
def add_student():
    student_data = (
        student_id_entry.get(),
        name_entry.get(),
        gender_var.get(),
        int(year_level_entry.get()),
        course_code_var.get()  # Get the selected course code from the dropdown
    )
    student_id = student_data[0]
    
    if student_id_exists(student_id):
        tkinter.messagebox.showwarning("Duplicate Student ID", "Student ID already exists!")
    else:
        create_student(student_data)
        refresh_students()

def edit_selected_student():
    selected_item = student_list.selection()
    if selected_item:
        student_id = student_list.item(selected_item, "values")[1]
        
        # Fetch student data from the database
        student_data = read_students()
        selected_student = None
        for student in student_data:
            if student[1] == student_id:
                selected_student = student
                break
        
        if selected_student:
            student_edit_dialog = tkinter.simpledialog.Toplevel()
            student_edit_dialog.title("Edit Student")
            
            # Student ID Label
            student_id_label = ttk.Label(student_edit_dialog, text="Student ID:")
            student_id_label.grid(row=0, column=0)
            
            # Display the student's ID using a Label
            student_id_display = ttk.Label(student_edit_dialog, text=selected_student[1])
            student_id_display.grid(row=0, column=1)
            
            # Name Label
            name_label = ttk.Label(student_edit_dialog, text="Name:")
            name_label.grid(row=1, column=0)
            name_entry = ttk.Entry(student_edit_dialog)
            name_entry.grid(row=1, column=1)
            name_entry.insert(0, selected_student[2])  # Populate with existing name
            
            # Gender Label
            gender_label = ttk.Label(student_edit_dialog, text="Gender:")
            gender_label.grid(row=2, column=0)
            gender_var = tk.StringVar(value=selected_student[3])  # Populate with existing gender
            gender_entry = ttk.Combobox(student_edit_dialog, textvariable=gender_var, values=["Male", "Female", "Other"])
            gender_entry.grid(row=2, column=1)
            
            # Year Level Label
            year_level_label = ttk.Label(student_edit_dialog, text="Year Level:")
            year_level_label.grid(row=3, column=0)
            year_level_entry = ttk.Entry(student_edit_dialog)
            year_level_entry.grid(row=3, column=1)
            year_level_entry.insert(0, selected_student[4])  # Populate with existing year level
            
            # Course Code Label
            course_code_label = ttk.Label(student_edit_dialog, text="Course Code:")
            course_code_label.grid(row=4, column=0)
            
            # Fetch course codes from the database and populate the course code dropdown
            courses = read_courses()
            course_codes = [course[1] for course in courses]
            course_code_var = tk.StringVar(value=selected_student[5])  # Populate with existing course code
            course_code_dropdown = ttk.Combobox(student_edit_dialog, textvariable=course_code_var, values=course_codes)
            course_code_dropdown.grid(row=4, column=1)
            
            def save_changes():
                new_name = name_entry.get()
                new_gender = gender_var.get()
                new_year_level = year_level_entry.get()
                new_course_code = course_code_var.get()
                
                if new_name and new_gender and new_year_level and new_course_code:
                    update_student((new_name, new_gender, new_year_level, new_course_code, selected_student[0]))
                    update_student_course(student_id, new_course_code)  # Update student's course code
                    refresh_students()  # Refresh the student list
                    student_edit_dialog.destroy()
            
            save_btn = ttk.Button(student_edit_dialog, text="Save Changes", command=save_changes)
            save_btn.grid(row=5, columnspan=2, pady=10)

def delete_selected_student():
    selected_item = student_list.selection()
    if selected_item:
        student_id = student_list.item(selected_item, "values")[1]
        delete_student(student_id)
        refresh_students()

def add_course():
    course_data = (
        course_code_entry.get(),
        course_entry.get(),
        college_entry.get()
    )
    course_code = course_data[0]
    
    if course_code_exists(course_code):
        tkinter.messagebox.showwarning("Duplicate Course Code", "Course code already exists!")
    else:
        create_course(course_data)
        refresh_courses()
        refresh_students()  # Update the student frame dropdown with the latest course codes

def edit_selected_course():
    selected_item = course_list.selection()
    if selected_item:
        course_code = course_list.item(selected_item, "values")[1]
        
        # Create a dialog to edit course information
        course_data = read_courses()
        selected_course = None
        for course in course_data:
            if course[1] == course_code:
                selected_course = course
                break
        
        if selected_course:
            course_edit_dialog = tkinter.simpledialog.Toplevel()
            course_edit_dialog.title("Edit Course")
            
            # Course Code Label
            course_code_label = ttk.Label(course_edit_dialog, text="Course Code:")
            course_code_label.grid(row=0, column=0)
            
            # Display the student's ID using a Label
            course_code_display = ttk.Label(course_edit_dialog, text=selected_course[1])
            course_code_display.grid(row=0, column=1)
            
            # Course Label
            course_label = ttk.Label(course_edit_dialog, text="Course:")
            course_label.grid(row=1, column=0)
            course_entry = ttk.Entry(course_edit_dialog)
            course_entry.grid(row=1, column=1)
            course_entry.insert(0, selected_course[2])  # Populate with existing course value
            
            # College Label
            college_label = ttk.Label(course_edit_dialog, text="College:")
            college_label.grid(row=2, column=0)
            college_entry = ttk.Entry(course_edit_dialog)
            college_entry.grid(row=2, column=1)
            college_entry.insert(0, selected_course[3])  # Populate with existing college value
            
            def save_changes():
                new_course_value = course_entry.get()
                new_college_value = college_entry.get()
                new_course_code = course_code_var.get()  # Get the edited course code

                if new_course_value and new_college_value and new_course_code:
                    update_course((new_course_value, new_college_value, selected_course[0]))
                    refresh_courses()
                    course_edit_dialog.destroy()

            save_btn = ttk.Button(course_edit_dialog, text="Save Changes", command=save_changes)
            save_btn.grid(row=3, columnspan=2, pady=10)

def delete_selected_course():
    selected_item = course_list.selection()
    if selected_item:
        course_code = course_list.item(selected_item, "values")[1]
        delete_course(course_code)
        refresh_courses()

def search_students_button():
    search_query = search_student_entry.get()
    search_results = search_students(search_query)
    student_list.delete(*student_list.get_children())
    for student in search_results:
        student_list.insert("", "end", values=student)

def search_courses_button():
    search_query = search_course_entry.get()
    search_results = search_courses(search_query)
    course_list.delete(*course_list.get_children())
    for course in search_results:
        course_list.insert("", "end", values=course)

def refresh_students():
    # Fetch the latest course codes from the database
    courses = read_courses()
    course_codes = [course[1] for course in courses]

    # Update the values in the course code dropdown
    course_code_dropdown['values'] = course_codes

    students = read_students()
    student_list.delete(*student_list.get_children())
    for student in students:
        student_list.insert("", "end", values=student)

def refresh_courses():
    courses = read_courses()
    course_list.delete(*course_list.get_children())
    for course in courses:
        course_list.insert("", "end", values=course)

def refresh_app():
    refresh_students()
    refresh_courses()

# Main GUI setup
root = tk.Tk()
root.title("Student Information System")

# Set grid weights to allow resizing of frames
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Create Student Frame
student_frame = ttk.LabelFrame(root, text="Students")
student_frame.grid(row=1, column=0, padx=10, pady=10)

student_id_label = ttk.Label(student_frame, text="Student ID:")
student_id_label.grid(row=0, column=0)
student_id_entry = ttk.Entry(student_frame)
student_id_entry.grid(row=0, column=1)

name_label = ttk.Label(student_frame, text="Name:")
name_label.grid(row=1, column=0)
name_entry = ttk.Entry(student_frame)
name_entry.grid(row=1, column=1)

gender_label = ttk.Label(student_frame, text="Gender:")
gender_label.grid(row=2, column=0)
gender_var = tk.StringVar(value="Male")
gender_entry = ttk.Combobox(student_frame, textvariable=gender_var, values=["Male", "Female"])
gender_entry.grid(row=2, column=1)

year_level_label = ttk.Label(student_frame, text="Year Level:")
year_level_label.grid(row=3, column=0)
year_level_entry = ttk.Entry(student_frame)
year_level_entry.grid(row=3, column=1)

course_code_label = ttk.Label(student_frame, text="Course Code:")
course_code_label.grid(row=4, column=0)
course_code_entry = ttk.Entry(student_frame)
course_code_entry.grid(row=4, column=1)

# Fetch course codes from the database and populate the course code dropdown
courses = read_courses()
course_codes = [course[1] for course in courses]
course_code_var = tk.StringVar(value=course_codes[1] if course_codes else "")
course_code_dropdown = ttk.Combobox(student_frame, textvariable=course_code_var, values=course_codes)
course_code_dropdown.grid(row=4, column=1)

add_student_btn = ttk.Button(student_frame, text="Add Student", command=add_student)
add_student_btn.grid(row=5, columnspan=2, pady=5)

student_list = ttk.Treeview(student_frame, columns=("ID", "Student ID", "Name", "Gender", "Year Level", "Course Code"), show="headings")
student_list.heading("ID", text="ID")
student_list.heading("Student ID", text="Student ID")
student_list.heading("Name", text="Name")
student_list.heading("Gender", text="Gender")
student_list.heading("Year Level", text="Year Level")
student_list.heading("Course Code", text="Course Code")
student_list.grid(row=6, column=0, columnspan=2, padx=5)

edit_student_btn = ttk.Button(student_frame, text="Edit Selected Student", command=edit_selected_student)
edit_student_btn.grid(row=5, column = 1, columnspan=2, pady=5)

delete_student_btn = ttk.Button(student_frame, text="Delete Selected Student", command=delete_selected_student)
delete_student_btn.grid(row=7, column = 1, columnspan=2, pady=5)

student_search_frame = ttk.LabelFrame(student_frame, text="Search Students")
student_search_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=10)  # Placed inside student_frame

search_student_entry = ttk.Entry(student_search_frame)
search_student_entry.grid(row=0, column=0, padx=5)

search_student_btn = ttk.Button(student_search_frame, text="Search Students", command=search_students_button)
search_student_btn.grid(row=0, column=1, padx=5)

# Create Course Frame
course_frame = ttk.LabelFrame(root, text="Courses")
course_frame.grid(row=4, column=0, padx=10, pady=10)

course_code_label = ttk.Label(course_frame, text="Course Code:")
course_code_label.grid(row=0, column=0)
course_code_entry = ttk.Entry(course_frame)
course_code_entry.grid(row=0, column=1)

course_label = ttk.Label(course_frame, text="Course:")
course_label.grid(row=1, column=0)
course_entry = ttk.Entry(course_frame)
course_entry.grid(row=1, column=1)

college_label = ttk.Label(course_frame, text="College:")
college_label.grid(row=2, column=0)
college_entry = ttk.Entry(course_frame)
college_entry.grid(row=2, column=1)

add_course_btn = ttk.Button(course_frame, text="Add Course", command=add_course)
add_course_btn.grid(row=3, columnspan=2, pady=5)

course_list = ttk.Treeview(course_frame, columns=("ID", "Course Code", "Course", "College"), show="headings")
course_list.heading("ID", text="ID")
course_list.heading("Course Code", text="Course Code")
course_list.heading("Course", text="Course")
course_list.heading("College", text="College")
course_list.grid(row=4, column=0, columnspan=2, padx=5)

edit_course_btn = ttk.Button(course_frame, text="Edit Selected Course", command=edit_selected_course)
edit_course_btn.grid(row=3, column = 1, columnspan=2, pady=5)

delete_course_btn = ttk.Button(course_frame, text="Delete Selected Course", command=delete_selected_course)
delete_course_btn.grid(row=5, column = 1, columnspan=2, pady=5)

course_search_frame = ttk.LabelFrame(course_frame, text="Search Courses")
course_search_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10)  # Placed inside course_frame

search_course_entry = ttk.Entry(course_search_frame)
search_course_entry.grid(row=0, column=0, padx=5)

search_course_btn = ttk.Button(course_search_frame, text="Search Courses", command=search_courses_button)
search_course_btn.grid(row=0, column=1, padx=5)

app_refresh_btn = ttk.Button(course_frame, text="Refresh App", command=refresh_app)
app_refresh_btn.grid(row=5, column=2, pady=10)

# Refresh data on startup
refresh_students()
refresh_courses()

root.mainloop()