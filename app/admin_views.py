from app import app
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re



app.secret_key = "Thisismysecretket"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'OnlineBookings_DB'
mysql = MySQL(app)


@app.route('/admin_login', methods = ['GET', "POST"])
def admin_login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['username'] = username
            message = 'Login successful!', 'success'
            return redirect(url_for('admin_dashboard'))
        else:
            message ='Login failed. Please check your credentials.', 'danger'
    return render_template("admin_login.html")


@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template("admin_dashboard.html")


# Fetching all doctors information from database
@app.route('/admin_adddoctors')
def admin_adddoctors():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM doctors")
    data = cur.fetchall()
    cur.close()
    return render_template("admin_adddoctors.html", doctors = data)


# Inserting Doctor Data to the database
@app.route('/insertDoctorData', methods = ['POST'])
def insertDoctorData():
    if request.method == "POST":
        flash("Doctor Successfully Added")
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        specialities = request.form['specialities']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO doctors (name, email, contact, specialities, password) VALUES (%s, %s, %s, %s, %s)", (name, email, contact, specialities, password))
        mysql.connection.commit()
        return redirect(url_for('admin_adddoctors'))











@app.route('/addNew_doctor', methods = ['GET', 'POST'])
def addNew_doctor():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'contact' in request.form and 'specialities' in request.form and 'password' in request.form:
         name = request.form['name']
         email = request.form['email']
         contact = request.form['contact']
         specialities = request.form['specialities']
         password = request.form['password']
         cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cur.execute('SELECT * FROM doctor WHERE email = % s', (email,))
         account = cur.fetchone()
         if account:
              message = 'Doctor already exists !'
         elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
              message = 'Invalid email address !'
         else:
            cur.execute('INSERT INTO doctor (name, email, contact, specialities, password) VALUES (% s, % s, % s, % s, % s)', (name, email, contact, specialities, password))
            mysql.connection.commit()
            message = 'Doctor Successful Added !'
    elif request.method == 'POST':
         message = 'Please fill out the form !'   
    return render_template("addNew_doctor.html", message=message)

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
