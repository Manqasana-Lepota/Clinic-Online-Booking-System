from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors  # Import MySQLdb cursors
from werkzeug.security import check_password_hash

app = Flask(__name__)  

admin = Blueprint("admin", __name__)  # Define Blueprint

app.secret_key = "Thisismysecretket" # Change this to a secure secret key

# MySQL Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "BookingSystem"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


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
    total_doctors = result['total']  # Extract the total count

    # Pass the total_doctors count to the template
    return render_template("AdminDashboard.html", total_doctors=total_doctors)


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

