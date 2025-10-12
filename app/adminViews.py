from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session
from app import mysql
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
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

# Admin Dashboard route
@admin.route("/admin/dashboard")
def AdminDashboard():
   # Fetch the total number of doctors from the database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT COUNT(*) AS total FROM doctors")
    result = cursor.fetchone()
    total_doctors = result['total']  

    # Fetch the total number of patients from the database (using raw SQL query)
    cursor.execute("SELECT COUNT(*) AS total FROM patients") 
    result_patients = cursor.fetchone()
    total_patients = result_patients['total']

    
    return render_template('AdminDashboard.html', total_doctors=total_doctors, total_patients=total_patients)


# Admin Manages Doctors route
@admin.route('/manage_doctors', methods=['GET', 'POST'])
def manage_doctors():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        firstname = request.form.get('firstname', '').strip()
        lastname = request.form.get('lastname', '').strip()
        specialization = request.form.get('specialization', '').strip()
        experience_years = request.form.get('experience_years', 0)
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
   
        if len(password) < 12 or len(password) > 16:
            flash("Password must be between 12 and 16 characters.", "danger")
            return redirect(url_for('admin.manage_doctors'))
        
        available_days = ', '.join(request.form.getlist('available_days[]'))

       
        password_to_save = password  

        filename = "default.png"
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename != "":
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        insert_query = """
        INSERT INTO doctors 
        (firstname, lastname, specialization, experience_years, available_days, email, username, password, profile_picture) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(insert_query, (
            firstname, lastname, specialization, experience_years, 
            available_days, email, username, password_to_save, filename
        ))

        mysql.connection.commit()
        flash("Doctor added successfully!", "success")
        return redirect(url_for('admin.manage_doctors'))

  
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    sort_by = request.args.get('sort_by', 'doctor_id')
    order = request.args.get('order', 'asc')
    offset = (page - 1) * per_page

    base_query = """
        SELECT * FROM doctors
        WHERE firstname LIKE %s OR lastname LIKE %s OR specialization LIKE %s
    """
    params = ('%' + search + '%', '%' + search + '%', '%' + search + '%')

    cursor.execute(f"SELECT COUNT(*) AS total FROM ({base_query}) AS t", params)
    total_records = cursor.fetchone()['total']
    total_pages = (total_records + per_page - 1) // per_page

    query = f"{base_query} ORDER BY {sort_by} {order} LIMIT %s OFFSET %s"
    cursor.execute(query, params + (per_page, offset))
    doctors = cursor.fetchall()
    cursor.close()

    return render_template(
        'AdminManagesDoctors.html',
        doctors=doctors,
        page=page,
        total_pages=total_pages,
        search=search,
        sort_by=sort_by,
        order=order
    )

# Admin Delete Doctor route
@admin.route("/delete_doctor/<int:doctor_id>", methods=["GET", "POST"])
def delete_doctor(doctor_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DELETE FROM doctors WHERE doctor_id = %s", (doctor_id,))
        mysql.connection.commit()
        cursor.close()
        flash("Doctor deleted successfully!", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error deleting doctor: {str(e)}", "danger")
    
    return redirect(url_for("admin.manage_doctors"))


# Admin Edit Doctor route
@admin.route('/edit_doctor/<int:doctor_id>', methods=['POST'])
def edit_doctor(doctor_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    specialization = request.form.get('specialization')
    experience_years = request.form.get('experience_years')
    email = request.form.get('email')
    username = request.form.get('username')

    
    selected_days = request.form.getlist('available_days[]')
    available_days = ', '.join(selected_days) if selected_days else ''

   
    password = request.form.get('password', '').strip()
    if password:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    else:
        password_hash = None 

   
    filename = None
    if 'profile_picture' in request.files:
        file = request.files['profile_picture']
        if file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

  
    update_query = """
        UPDATE doctors
        SET firstname=%s, lastname=%s, specialization=%s, experience_years=%s,
            available_days=%s, email=%s, username=%s
    """
    params = [firstname, lastname, specialization, experience_years, available_days, email, username]

    if password_hash:
        update_query += ", password=%s"
        params.append(password_hash)

    if filename:
        update_query += ", profile_picture=%s"
        params.append(filename)

    update_query += " WHERE doctor_id=%s"
    params.append(doctor_id)

    cursor.execute(update_query, params)
    mysql.connection.commit()
    flash("Doctor details updated successfully!", "success")
    return redirect(url_for('admin.manage_doctors'))






# Admin Manage Patients route
@admin.route('/manage_patients')
def manage_patients():
    # Get query parameters
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10  
    sort_by = request.args.get('sort_by', 'patient_id')  
    order = request.args.get('order', 'asc') 

    offset = (page - 1) * per_page
    cursor = mysql.connection.cursor()

    # Prepare base query
    base_query = "SELECT * FROM patients WHERE firstname LIKE %s OR lastname LIKE %s OR username LIKE %s"
    params = ('%' + search + '%', '%' + search + '%', '%' + search + '%')

    # Count total records
    cursor.execute(f"SELECT COUNT(*) as total FROM ({base_query}) as t", params)
    total_records = cursor.fetchone()['total']
    total_pages = (total_records + per_page - 1) // per_page  # ceil division

    # Fetch current page with sorting
    query = f"{base_query} ORDER BY {sort_by} {order} LIMIT %s OFFSET %s"
    cursor.execute(query, params + (per_page, offset))
    patients = cursor.fetchall()

    return render_template(
        'AdminManagePatients.html',
        patients=patients,
        page=page,
        total_pages=total_pages,
        search=search,
        sort_by=sort_by,
        order=order
    )
  
# Admin Delete Patients
@admin.route("/delete_patient/<int:patient_id>", methods=["GET", "POST"])
def delete_patient(patient_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM patients WHERE patient_id = %s", (patient_id,))
        mysql.connection.commit()
        cur.close()
        flash("Patient deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting patient: {str(e)}", "danger")
    return redirect(url_for("admin.manage_patients"))




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