from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session
from app import mysql
from flask_mysqldb import MySQL
import MySQLdb.cursors  # Import MySQLdb cursors
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
import bcrypt
from datetime import datetime


admin = Blueprint("admin", __name__)  # Define Blueprint


# Admin Login Route
@admin.route("/admin/login", methods=["GET", "POST"])
def AdminLogin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Fetch admin data
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM admin WHERE username = %s", (username,))
        admin_data = cur.fetchone()
        cur.close()

        print("Admin Data:", admin_data)  # Debugging - See what is fetched

        if admin_data:
            stored_hashed_password = admin_data["password_hash"]  # Correct column name
            print("Stored Hashed Password:", stored_hashed_password)  # Debugging

            # Directly compare passwords if stored in plain text
            if stored_hashed_password == password:  # Use this if passwords are NOT hashed
                session["admin_logged_in"] = True
                session["admin_username"] = admin_data["username"]
                flash("Login successful!", "success")
                return redirect(url_for('admin.AdminDashboard'))
            else:
                flash("Invalid username or password", "danger")
        else:
            flash("Invalid username or password", "danger")

    return render_template('AdminLogin.html')


@admin.route("/admin/dashboard")
def AdminDashboard():
   # Fetch the total number of doctors from the database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT COUNT(*) AS total FROM doctors")
    result = cursor.fetchone()
    total_doctors = result['total']  # Extract the total count of doctors

    # Fetch the total number of patients from the database (using raw SQL query)
    cursor.execute("SELECT COUNT(*) AS total FROM patients")  # Assuming your table name is 'patients'
    result_patients = cursor.fetchone()
    total_patients = result_patients['total']

    # Render the template and pass both the total_doctors and total_patients values
    return render_template('AdminDashboard.html', total_doctors=total_doctors, total_patients=total_patients)

@admin.route('/admin/adminManagesDoctors', methods=['GET', 'POST'])
def AdminManagesDoctors():
    message = ''
    doctors = []  # Initialize doctors list

    # Fetch doctors data from the database (GET request)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM doctors")  # Fetch all doctors
    doctors = cursor.fetchall()  # Store the result in a list of dictionaries
    cursor.close()  # Close the cursor after fetching data

    if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'specialization' in request.form and 'experience_years' in request.form and 'available_days[]' in request.form and 'username' in request.form and 'password' in request.form:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        specialization = request.form['specialization']
        experience_years = request.form['experience_years']
        available_days = ', '.join(request.form.getlist('available_days[]'))  # Convert list to string
        username = request.form['username']
        password = request.form['password']
       
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM doctors WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            message = 'Doctor already exists!'
        elif not firstname or not lastname or not specialization or not experience_years or not available_days or not username or not password:
            message = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO doctors (firstname, lastname, specialization, experience_years, available_days, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                           (firstname, lastname, specialization, experience_years, available_days, username, password))
            mysql.connection.commit()
            message = 'Doctor Registered Successfully!'

    elif request.method == 'POST':
        message = 'Please fill out the form!'

    return render_template("AdminManagesDoctors.html", message=message, doctors=doctors)

@admin.route('/admin/edit_doctor/<doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    # Fetch the doctor by doctor_id
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM doctors WHERE doctor_id = %s", (doctor_id,))
    doctor = cursor.fetchone()
    cursor.close()

    if not doctor:
        flash("Doctor not found!", "danger")
        return redirect(url_for('admin.AdminManagesDoctors'))

    # Handle form submission (if POST)
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        specialization = request.form['specialization']
        experience_years = request.form['experience_years']
        available_days = ', '.join(request.form.getlist('available_days[]'))
        username = request.form['username']
        password = request.form['password']

        # Update doctor details
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''UPDATE doctors 
                          SET firstname = %s, lastname = %s, specialization = %s, 
                              experience_years = %s, available_days = %s, 
                              username = %s, password = %s 
                          WHERE doctor_id = %s''', 
                       (firstname, lastname, specialization, experience_years, 
                        available_days, username, password, doctor_id))
        mysql.connection.commit()
        cursor.close()

        flash("Doctor details updated successfully!", "success")
        return redirect(url_for('admin.AdminManagesDoctors'))

    return render_template("edit_doctor.html", doctor=doctor)

@admin.route('/admin/delete_doctor/<doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    # Delete the doctor by doctor_id
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM doctors WHERE doctor_id = %s", (doctor_id,))
    mysql.connection.commit()
    cursor.close()

    flash("Doctor deleted successfully!", "success")
    return redirect(url_for('admin.AdminManagesDoctors'))


@admin.route('/admin/adminManagePatients', methods=['GET', 'POST'])
def AdminManagePatients():
    # Open a cursor to interact with the MySQL database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Execute the query to fetch all patients
    cursor.execute("SELECT * FROM patients")  # Adjust the table name if necessary
    patients = cursor.fetchall()  # Fetch all patient data as a list of dictionaries
    
    # Close the cursor
    cursor.close()
    
    # Render the template and pass the patients data
    return render_template('AdminManagePatients.html', patients=patients)



@admin.route("/admin/adminaddpatient", methods=["POST"])
def AdminAddPatient():
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        DateOfBirth = request.form["DateOfBirth"]
        age = request.form["age"]
        gender = request.form["gender"]
        marital_status = request.form["marital_status"]
        email = request.form["email"]
        contact = request.form["contact"]
        address = request.form["address"]
        password = request.form["password"]
        
        # Insert data into the database
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO patients (firstname, lastname, DateOfBirth, age, gender, marital_status, email, contact, address, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (firstname, lastname, DateOfBirth, age, gender, marital_status, email, contact, address, password))
        mysql.connection.commit()
        cursor.close()

        flash("Patient added successfully!", "success")
        return redirect(url_for('admin.AdminManagePatients'))  # Redirect back to the patient management page
    





# Update the route name to AdminDeletePatient
@admin.route('/admin/delete_patient', methods=['POST'])
def AdminDeletePatient():
    patient_id = request.form['patient_id'] if 'patient_id' in request.form else None
    
    # Debugging: Print received data
    print(f"Received patient_id: {patient_id}") 
     

    if not patient_id:
        flash("Error: No patient ID received.", "danger")
        return redirect(url_for('admin.AdminManagePatients'))

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM patients WHERE patient_id = %s", (patient_id,))
        mysql.connection.commit()
        cursor.close()

        flash("Patient deleted successfully!", "success")
    except Exception as e:
        flash(f"Error occurred while deleting patient: {str(e)}", "danger")

    return redirect(url_for('admin.AdminManagePatients'))



@admin.route('/admin/edit_patient', methods=['POST'])
def AdminEditPatient():
    # Print the form data to debug
    print("Form Data:", request.form)

    patient_id = request.form['patient_id'] if 'patient_id' in request.form else None
    
    if not patient_id:
        flash("Error: No patient ID received.", "danger")
        return redirect(url_for('admin.AdminManagePatients'))  # Redirect back to the patients page

    try:
        # Update patient details based on form data
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE patients SET firstname = %s, lastname = %s, DateOfBirth = %s, age = %s, gender = %s, marital_status = %s, address = %s, email = %s, contact = %s, password = %s WHERE patient_id = %s", 
                       (request.form['firstname'],  # First Name
                        request.form['lastname'],  # Last Name
                        request.form['DateOfBirth'],
                        request.form['age'],
                        request.form['gender'],
                        request.form['marital_status'],
                        request.form['address'],
                        request.form['email'],
                        request.form['contact'],
                        request.form['password'],
                        patient_id))

        mysql.connection.commit()
        cursor.close()

        flash("Patient updated successfully!", "success")
    except Exception as e:
        flash(f"Error occurred while updating patient: {str(e)}", "danger")

    return redirect(url_for('admin.AdminManagePatients'))




@admin.route('/logout')
def logout():
    # Remove the user session (if you're using Flask-Login or sessions)
    session.pop('user_id', None)  # Replace 'user_id' with your session variable
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('loginroles'))  # Redirect to the login page (or another page)