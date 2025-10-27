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
        cursor.close()

        if doctor and doctor['password'] == password:  # or use check_password_hash if hashed
            session['doctor_id'] = doctor['doctor_id']
            session['firstname'] = doctor['firstname']
            session['lastname'] = doctor['lastname']
            session['profile_picture'] = doctor['profile_picture']
            session['specialization'] = doctor['specialization']

            flash("Login successful!", "success")
            return redirect(url_for('doctor.DoctorDashboard'))
        else:
            flash("Invalid credentials, please try again.", "danger")

    return render_template('DoctorLogin.html')


@doctor.route('/doctor-dashboard', methods=['GET', 'POST'], endpoint="DoctorDashboard")
def DoctorDashboard():
    if 'doctor_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('loginroles.universal_login'))


    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM doctors WHERE doctor_id = %s", (session['doctor_id'],))
    doctor = cursor.fetchone()
    cursor.close()

    firstname = doctor['firstname'] if doctor else "Doctor"
    return render_template('DoctorDashboard.html', firstname=firstname, doctor=doctor)


@doctor.route('/update_profile', methods=['POST'])
def update_profile():
    doctor_id = session.get('doctor_id')

    if not doctor_id:
        flash("Doctor not found or not logged in.", "danger")
        return redirect(url_for('doctor.DoctorLogin'))

    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    specialization = request.form.get('specialization')

    # Handle profile picture
    profile_pic = request.files.get('profile_pic')
    filename = None
    if profile_pic and profile_pic.filename != "":
        filename = secure_filename(profile_pic.filename)
        upload_path = os.path.join('static/uploads', filename)
        profile_pic.save(upload_path)

    # Handle password
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    cursor = mysql.connection.cursor()

    # If changing password
    if current_password and new_password and confirm_password:
        cursor.execute("SELECT password FROM doctors WHERE doctor_id=%s", (doctor_id,))
        doctor = cursor.fetchone()
        if doctor and doctor['password'] == current_password:  # Or check_password_hash if hashed
            if new_password == confirm_password:
                password_to_save = new_password  # Or generate_password_hash(new_password)
                cursor.execute("""
                    UPDATE doctors
                    SET password=%s
                    WHERE doctor_id=%s
                """, (password_to_save, doctor_id))
            else:
                flash("New passwords do not match.", "danger")
                return redirect(url_for('doctor.DoctorDashboard'))
        else:
            flash("Incorrect current password.", "danger")
            return redirect(url_for('doctor.DoctorDashboard'))

    # Update other info
    if filename:
        cursor.execute("""
            UPDATE doctors
            SET firstname=%s, lastname=%s, email=%s, phone=%s, specialization=%s, profile_picture=%s
            WHERE doctor_id=%s
        """, (firstname, lastname, email, phone, specialization, filename, doctor_id))
    else:
        cursor.execute("""
            UPDATE doctors
            SET firstname=%s, lastname=%s, email=%s, phone=%s, specialization=%s
            WHERE doctor_id=%s
        """, (firstname, lastname, email, phone, specialization, doctor_id))

    mysql.connection.commit()
    cursor.close()

    # Update session info
    session['firstname'] = firstname
    session['lastname'] = lastname
    if filename:
        session['profile_picture'] = filename

    flash("Profile updated successfully!", "success")
    return redirect(url_for('doctor.DoctorDashboard'))



@doctor.route('/schedule', methods=['GET', 'POST'])
def doctor_schedule():
    doctor_id = session.get('doctor_id')  # Get the logged-in doctor

    if request.method == 'POST':
        day = request.form['day']
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO doctor_schedule (doctor_id, day, start_time, end_time)
            VALUES (%s, %s, %s, %s)
        """, (doctor_id, day, start_time, end_time))
        mysql.connection.commit()
        cursor.close()

        flash("Schedule added successfully!", "success")
        return redirect(url_for('doctor.doctor_schedule'))

    # Fetch existing schedules
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM doctor_schedule WHERE doctor_id = %s", (doctor_id,))
    schedules = cursor.fetchall()

    # Fetch doctor info for template
    cursor.execute("SELECT * FROM doctors WHERE doctor_id = %s", (doctor_id,))
    doctor_info = cursor.fetchone()
    cursor.close()

    return render_template(
        "DoctorDashboard.html",
        schedules=schedules,
        doctor=doctor_info  # Pass doctor info to template
    )


@doctor.route("/schedule/edit/<int:id>", methods=["POST"])
def edit_schedule(id):
    day = request.form["day"]
    start_time = request.form["start_time"]
    end_time = request.form["end_time"]

    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE doctor_schedule
        SET day=%s, start_time=%s, end_time=%s
        WHERE id=%s
    """, (day, start_time, end_time, id))
    mysql.connection.commit()
    cursor.close()

    flash("Schedule updated successfully!", "success")
    return redirect(url_for("doctor.doctor_schedule"))


@doctor.route('/schedule/delete/<int:id>', methods=['GET'])
def delete_schedule(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM doctor_schedule WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash("Schedule deleted.", "info")
    return redirect(url_for('doctor.doctor_schedule'))


