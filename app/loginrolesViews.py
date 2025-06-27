from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import mysql

loginroles = Blueprint('loginroles', __name__)

@loginroles.route('/login', methods=['GET', 'POST'])
def login():
    # login logic here
    return render_template('loginroles.html')

@loginroles.route('/universal-login', methods=['GET'])
def show_universal_login():
    role = request.args.get('role') 
    return render_template('universal_login.html', selected_role=role)


@loginroles.route('/universal-login', methods=['POST'])
def universal_login():
    user_type = request.form.get('user_type')
    username = request.form.get('username')
    password = request.form.get('password')

    cursor = mysql.connection.cursor()

    if user_type == "admin":
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
        
        user = cursor.fetchone()
        if user:
            session['user_type'] = 'admin'
            session['username'] = username
            return redirect(url_for('admin.AdminDashboard'))
        else:
            flash("Invalid Admin credentials")

    elif user_type == "doctor":
        cursor.execute("SELECT * FROM doctors WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            session['user_type'] = 'doctor'
            session['username'] = username

            firstname = user['firstname'].split()[0]

            firstname = firstname.split()[0] if firstname else 'Patient'
            session['firstname'] = firstname
            return redirect(url_for('doctor.DoctorDashboard'))
        else:
            flash("Invalid Doctor credentials")

    elif user_type == "patient":
        cursor.execute("SELECT * FROM patients WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            session['user_type'] = 'patient'
            session['username'] = username

            firstname = user['firstname'].split()[0]

            firstname = firstname.split()[0] if firstname else 'Patient'
            session['firstname'] = firstname
            return redirect(url_for('patient.PatientDashboard'))
        else:
            flash("Invalid Patient credentials")

    else:
        flash("Please select a valid user type")

    return render_template('universal_login.html', selected_role=user_type)

