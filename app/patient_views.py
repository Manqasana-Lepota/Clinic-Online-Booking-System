from app import app
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app.secret_key = "Thisismysecretket"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'BookingSystem'
mysql = MySQL(app)


@app.route('/PatientLogin', methods = ['GET', 'POST'])
def PatientLogin():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM patients WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['patient_id'] = user['patient_id']
            session['firstname'] = user['firstname']
            session['lastname'] = user['lastname']
            session['DateOfBirth'] = user['DateOfBirth']
            session['age'] = user['age']
            session['gender'] = user['gender']
            session['marital_status'] = user['marital_status']
            session['email'] = user['email']
            session['contact'] = user['contact']
            session['address'] = user['address']
            message = 'Logged in successfully !'
            return redirect(url_for('PatientDashboard'))
        else:
            message = 'Please enter correct email / password'
    return render_template("PatientLogin.html", message = message)


@app.route('/PatientRegistrationForm', methods = ['GET', 'POST'])
def PatientRegistrationForm():
    message = ''
    if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'DateOfBirth' in request.form and 'age' in request.form and 'gender' in request.form and 'marital_status' in request.form and 'email' in request.form and 'contact' in request.form and 'address'in request.form and 'password' in request.form  and 'confirm_password' in request.form:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        DateOfBirth = request.form['DateOfBirth']
        age = request.form['age']
        gender = request.form['gender']
        marital_status = request.form['marital_status']
        email = request.form['email']
        contact = request.form['contact']
        address = request.form['address']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
       
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM patients WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            message = 'User already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address !'
        elif not firstname or not lastname or not DateOfBirth or not age or not gender or not marital_status or not password or not confirm_password or not email or not contact or not address:
            message = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO patients (firstname, lastname, DateOfBirth, age, gender, marital_status, email, contact, address, password, confirm_password) VALUES (% s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s )', (firstname, lastname, DateOfBirth, age, gender, marital_status, email,contact, address, password, confirm_password))
            mysql.connection.commit()
            message = 'Patient Registered Successful !'
    elif request.method == 'POST':
        message = 'Please fill out the form !'
    return render_template("PatientRegistrationForm.html", message = message)


@app.route('/PatientDashboard')
def PatientDashboard():
    return render_template("PatientDashboard.html")


@app.route('/BookAppointmentForm')
def BookAppointmentForm():
    return render_template("BookAppointmentForm.html")


# Fetching all patients information from database
@app.route('/patient_details')
def patient_details():
    return render_template("patient_details.html")
