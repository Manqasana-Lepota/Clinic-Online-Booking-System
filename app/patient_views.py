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


@app.route('/patient_login', methods = ['GET', 'POST'])
def patient_login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM patient WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['patientid'] = user['patientid']
            session['firstname'] = user['firstname']
            session['lastname'] = user['lastname']
            session['email'] = user['email']
            session['contact'] = user['contact']
            session['address'] = user['address']
            message = 'Logged in successfully !'
            return redirect(url_for('patient_dashboard'))
        else:
            message = 'Please enter correct email / password'
    return render_template("patient_login.html", message = message)


@app.route('/patient_registration', methods = ['GET', 'POST'])
def patient_registration():
    message = ''
    if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'email' in request.form and 'password' in request.form and 'contact' in request.form and 'address'in request.form:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        contact = request.form['contact']
        address = request.form['address']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM patient WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            message = 'User already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address !'
        elif not firstname or not lastname or not password or not email or not contact or not address:
            message = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO patient (firstname, lastname, email, password, contact, address) VALUES (% s, % s, % s, % s, % s, % s)', (firstname, lastname, email, password, contact, address))
            mysql.connection.commit()
            message = 'Patient Registered Successful !'
    elif request.method == 'POST':
        message = 'Please fill out the form !'
    return render_template("patient_registration.html", message = message)


@app.route('/patient_dashboard')
def patient_dashboard():
    return render_template("patient_dashboard.html")


# Fetching all patients information from database
@app.route('/patient_details')
def patient_details():
    return render_template("patient_details.html")
