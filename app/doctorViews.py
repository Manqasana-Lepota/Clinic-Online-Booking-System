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


