from flask import Flask, Blueprint, render_template, redirect, request, url_for, session, flash
from app import mysql
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

patient = Blueprint('patient', __name__)


@patient.route('/PatientDashboard')
def PatientDashboard():
    if 'username' not in session:
        return redirect(url_for('universal_login'))

    firstname = session.get('firstname', 'Patient')
    return render_template("PatientDashboard.html", firstname=firstname)
   

@patient.route('/PatientsRegisterForm', methods = ['GET', 'POST'])
def PatientsRegisterForm():
    return render_template("PatientsRegisterForm.html")


@patient.route('/PatientRegistrationForm', methods = ['GET', 'POST'])
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
    return render_template("patient.PatientRegistrationForm.html", message = message)










