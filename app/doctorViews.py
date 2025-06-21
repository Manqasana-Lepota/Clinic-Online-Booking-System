from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session
from app import mysql
from flask_mysqldb import MySQL
import MySQLdb.cursors  # Import MySQLdb cursors
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask import current_app
import re

# Define Blueprint for Doctor
doctor = Blueprint('doctor', __name__)



# Upload folder config
UPLOAD_FOLDER = 'static/uploads'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


@doctor.route('/doctor-login', methods=['GET', 'POST'], endpoint="DoctorLogin")
def DoctorLogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM doctors WHERE username = %s", (username,))
        doctor = cursor.fetchone()

        if doctor and doctor['password'] == password:
            session['doctor_id'] = doctor['doctor_id']
            session['firstname'] = doctor['firstname']
            session['lastname'] = doctor['lastname']
            session['profile_picture'] = doctor['profile_picture']
            session['specialization'] = doctor['specialization']
           

            flash("Login successful!", "success")
            return redirect(url_for('doctor.DoctorDashboard'))
        else:
            flash("Invalid credentials, please try again.", "danger")

        cursor.close()

    return render_template('DoctorLogin.html')


@doctor.route('/doctor-dashboard', methods=['GET', 'POST'], endpoint="DoctorDashboard")
def DoctorDashboard():
    if 'doctor_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('doctor.DoctorLogin'))

    doctor_id = session['doctor_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        # Get form data
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        specialization = request.form['specialization']
        experience_years = request.form['experience_years']
        available_days = request.form['available_days']
        username = request.form['username']

        # Update the database
        cursor.execute("""
            UPDATE doctors 
            SET firstname=%s, lastname=%s, specialization=%s, 
                experience_years=%s, available_days=%s, username=%s 
            WHERE doctor_id=%s
        """, (firstname, lastname, specialization, experience_years, available_days, username, doctor_id))

        mysql.connection.commit()

        # Update session values
        session['firstname'] = firstname
        session['lastname'] = lastname
        session['specialization'] = specialization

        flash("Doctor profile updated successfully!", "success")
        return redirect(url_for('doctor.DoctorDashboard'))

    # Fetch doctor data from DB
    cursor.execute("SELECT * FROM doctors WHERE doctor_id = %s", (doctor_id,))
    doctor = cursor.fetchone()
    cursor.close()

    return render_template('DoctorDashboard.html', doctor=doctor)


@doctor.route('/update-profile-pic', methods=['POST'])
def update_profile_pic():
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file.filename != '':
            filename = secure_filename(file.filename)

            # Ensure upload folder is correct
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            # Update DB
            doctor_id = session.get('doctor_id')
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE doctors SET profile_picture = %s WHERE doctor_id = %s", (filename, doctor_id))
            mysql.connection.commit()
            cursor.close()

            # Update session (optional)
            session['profile_picture'] = filename

            flash("Profile picture updated!", "success")
    else:
        flash("No file uploaded", "warning")

    return redirect(url_for('doctor.DoctorDashboard'))

def is_strong_password(password):
    return re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&+=!]).{8,}$', password)

@doctor.route('/change-password', methods=['POST'], endpoint='change_doctor_password')
def change_doctor_password():
    if 'doctor_id' not in session:
        flash("You must be logged in to change your password.", "warning")
        return redirect(url_for('doctor.DoctorLogin'))

    doctor_id = session['doctor_id']
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT password FROM doctors WHERE doctor_id = %s", (doctor_id,))
    doctor = cursor.fetchone()

    if not doctor or doctor['password'] != current_password:
        flash("Current password is incorrect.", "danger")
        return redirect(url_for('doctor.DoctorDashboard'))

    if new_password != confirm_password:
        flash("New passwords do not match.", "warning")
        return redirect(url_for('doctor.DoctorDashboard'))

    # Strong password check here
    if not is_strong_password(new_password):
        flash("Password must be at least 8 characters long and include uppercase, lowercase, a number, and a special character.", "danger")
        return redirect(url_for('doctor.DoctorDashboard'))

    # Save new password
    cursor.execute("UPDATE doctors SET password = %s WHERE doctor_id = %s", (new_password, doctor_id))
    mysql.connection.commit()
    cursor.close()

    flash("Password changed successfully!", "success")
    return redirect(url_for('doctor.DoctorDashboard'))