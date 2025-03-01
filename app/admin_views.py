from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "Thisismysecretket" # Change this to a secure secret key

# MySQL Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "BookingSystem"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

# Admin Login Route
@app.route("/admin/login", methods=["GET", "POST"])
def AdminLogin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admin WHERE username = %s", (username,))
        admin = cur.fetchone()
        cur.close()

        if admin and check_password_hash(admin["password"], password):  # Checking hashed password
            session["admin_logged_in"] = True
            session["admin_username"] = admin["username"]
            flash("Login successful!", "success")
            return redirect(url_for('AdminDashboard'))
        else:
            flash("Invalid username or password", "danger")

    return render_template('AdminLogin.html')


@app.route('/AdminDashboard')
def AdminDashboard():
    return render_template("AdminDashboard.html")



# Fetching all doctors information from database    
@app.route('/Admin_Doctors_Page')
def Admin_Doctors_Page():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM doctors")
        data = cur.fetchall()
        return render_template("Admin_Doctors_Page.html", data=data)
    except Exception as e:
        print(f"Error: {e}")
        flash("An error occurred while fetching data from the database.", 'error')
        return render_template("Admin_Doctors_Page.html", data=None)
    finally:
        # Ensure that the database connection is closed in all cases
        if cur:
            cur.close()
    

# Inserting Doctor Data to the database
@app.route('/Admin_Insert_Doctor', methods = ['POST'])
def Admin_Insert_Doctor():
     if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'contact' in request.form and 'specialities' in request.form and 'password' in request.form:
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        specialities = request.form['specialities']
        password = request.form['password']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM doctors WHERE email = % s', (email,))
        account = cur.fetchone()
        if account:
              flash('Doctor already exists !', 'warning')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
             flash('Invalid email address !', 'error')
        elif not name or not email or not contact or not specialities or not password:
             flash('Please fill out the form !', 'warning')
        else:
             cur.execute("INSERT INTO doctors (name, email, contact, specialities, password) VALUES (%s, %s, %s, %s, %s)", (name, email, contact, specialities, password))
             mysql.connection.commit()
             flash('New Doctor Successfully Added !', 'success')
        return redirect(url_for('Admin_Doctors_Page'))
     return 'Invalid request method'
     



@app.route('/Admin_Patients_Page')
def Admin_Patients_Page():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM patient")
        data = cur.fetchall()
        return render_template("Admin_Patients_Page.html", patient=data)
    except Exception as e:
        print(f"Error: {e}") 
        return "An error occurred."
    finally:
        if cur:
            cur.close()
















@app.route('/admin_patientslist')
def admin_patientslist():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM patient")
    data = cur.fetchall()
    cur.close()
    return render_template("admin_patientslist.html", patient = data)










@app.route('/view_doctor')
def view_doctor():
    return render_template("view_doctor.html")
