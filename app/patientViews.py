from flask import Blueprint, render_template, redirect, request, url_for, session, flash, current_app, jsonify
from app import mysql
import MySQLdb.cursors
from datetime import datetime
import re
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

patient = Blueprint('patient', __name__)

# Define Time Slot
ALL_TIME_SLOTS = [
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00"
]



@patient.route('/PatientDashboard')
def PatientDashboard():
    if 'username' not in session:
        return redirect(url_for('loginroles.universal_login'))

    firstname = session.get('firstname', 'Patient')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch doctors from database
    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()

    doctors_count = len(doctors)

    return render_template(
        "PatientDashboard.html",
        firstname=firstname,
        doctors=doctors,
        doctors_count=doctors_count
    )





   
@patient.route('/PatientsRegisterForm', methods=['GET', 'POST'])
def PatientsRegisterForm():
    message = ''
    
    if request.method == 'POST':
        # Basic personal info
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        date_of_birth = request.form.get('DateOfBirth')
        age = request.form.get('age')
        gender = request.form.get('gender')
        marital_status = request.form.get('marital_status')
        national_id = request.form.get('national_id')

        # Contact
        email = request.form.get('email')
        contact = request.form.get('contact')
        address = request.form.get('address')

        # Login
        username = request.form.get('username')
        password = request.form.get('password')

        # Medical
        medical_aid_number = request.form.get('medical_aid_number')
        blood_type = request.form.get('blood_type')
        allergies = request.form.get('allergies')
        chronic_conditions = request.form.get('chronic_conditions')

        # Emergency Contact
        emergency_contact_name = request.form.get('emergency_contact_name')
        emergency_contact_relationship = request.form.get('emergency_contact_relationship')
        emergency_contact_phone = request.form.get('emergency_contact_phone')

        # File upload
        profile_image = request.files.get('profile_image')
        filename = None
        
        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)  # Make folder if it doesn't exist
            profile_image.save(os.path.join(upload_folder, filename))

        # Basic validation
        if not all([firstname, lastname, date_of_birth, age, gender, marital_status, email, contact, address, username, password]):
            message = 'Please fill out all required fields!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM patients WHERE email = %s', (email,))
            account = cursor.fetchone()

            if account:
                message = 'An account with this email already exists.'
            else:
                cursor.execute('''
                    INSERT INTO patients (
                        firstname, lastname, DateOfBirth, age, gender, marital_status,
                        national_id, email, contact, address,
                        username, password,
                        medical_aid_number, blood_type, allergies, chronic_conditions,
                        emergency_contact_name, emergency_contact_relationship, emergency_contact_phone,
                        profile_image
                    ) VALUES (%s, %s, %s, %s, %s, %s,
                              %s, %s, %s, %s,
                              %s, %s,
                              %s, %s, %s, %s,
                              %s, %s, %s,
                              %s)
                ''', (
                    firstname, lastname, date_of_birth, age, gender, marital_status,
                    national_id, email, contact, address,
                    username, password,
                    medical_aid_number, blood_type, allergies, chronic_conditions,
                    emergency_contact_name, emergency_contact_relationship, emergency_contact_phone,
                    filename
                ))
                mysql.connection.commit()
                return redirect(url_for('loginroles.universal_login'))

    return render_template("PatientsRegisterForm.html", message=message)

# Profile Route
@patient.route('/profile')
def PatientProfile():
    if 'username' not in session:
        return redirect(url_for('loginroles.universal_login'))

    username = session['username']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch all patient info
    cursor.execute("SELECT * FROM patients WHERE username = %s", (username,))
    patient = cursor.fetchone()

    if not patient:
        flash("Patient profile not found!", "danger")
        return redirect(url_for('patient.PatientDashboard'))

    return render_template("PatientProfile.html", patient=patient)

# Edit Patient Profile
@patient.route('/edit_profile', methods=['GET', 'POST'])
def EditProfile():
    if 'username' not in session:
        return redirect(url_for('loginroles.universal_login'))

    username = session['username']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch current patient data
    cursor.execute("SELECT * FROM patients WHERE username = %s", (username,))
    patient = cursor.fetchone()

    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        contact = request.form.get('contact')
        address = request.form.get('address')
        medical_aid_number = request.form.get('medical_aid_number')
        blood_type = request.form.get('blood_type')
        allergies = request.form.get('allergies')
        chronic_conditions = request.form.get('chronic_conditions')

        # Handle profile image
        profile_image = request.files.get('profile_image')
        filename = patient['profile_image']  # default to existing filename

        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            profile_image.save(os.path.join(upload_folder, filename))

        # Update patient info in DB
        cursor.execute("""
            UPDATE patients
            SET firstname=%s, lastname=%s, email=%s, contact=%s, address=%s,
                medical_aid_number=%s, blood_type=%s, allergies=%s, chronic_conditions=%s,
                profile_image=%s
            WHERE username=%s
        """, (
            firstname, lastname, email, contact, address,
            medical_aid_number, blood_type, allergies, chronic_conditions,
            filename, username
        ))
        mysql.connection.commit()
        return redirect(url_for('patient.PatientProfile'))

    return render_template('EditPatientProfile.html', patient=patient)

# Route To Get Available Slot
@patient.route('/get_available_slots')
def get_available_slots():
    doctor_id = request.args.get('doctor_id')
    date = request.args.get('date')

    cursor = mysql.connection.cursor()

    # Get already booked times
    cursor.execute("""
        SELECT appointment_time 
        FROM appointments
        WHERE doctor_id = %s AND appointment_date = %s
    """, (doctor_id, date))

    booked_slots = cursor.fetchall()
    cursor.close()

    # Convert DB results to list of strings
    booked_times = [str(slot[0])[:5] for slot in booked_slots]

    # Remove booked slots from all slots
    available_slots = [slot for slot in ALL_TIME_SLOTS if slot not in booked_times]

    return jsonify(available_slots)


# Patient Booking Route
@patient.route('/book_appointment', methods=['POST'])
def book_appointment():
    try:
        patient_id = session.get('patient_id')  # logged-in user
        doctor_id = request.form['doctor_id']
        date = request.form['appointment_date']
        time = request.form['appointment_time']

        cursor = mysql.connection.cursor()

        # 🔒 1. Prevent double booking (same doctor, date, time)
        cursor.execute("""
            SELECT * FROM appointments
            WHERE doctor_id = %s
            AND appointment_date = %s
            AND appointment_time = %s
        """, (doctor_id, date, time))

        existing = cursor.fetchone()

        if existing:
            flash("❌ This time slot is already booked. Please choose another.", "danger")
            return redirect(url_for('patient.PatientDashboard'))

        # 💾 2. Insert booking
        cursor.execute("""
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time)
            VALUES (%s, %s, %s, %s)
        """, (patient_id, doctor_id, date, time))

        mysql.connection.commit()
        cursor.close()

        flash("✅ Appointment booked successfully!", "success")
        return redirect(url_for('patient.PatientDashboard'))

    except Exception as e:
        flash(f"⚠️ Error: {str(e)}", "danger")
        return redirect(url_for('patient.PatientDashboard'))


# Patient Appointments Route
@patient.route('/my_appointments')
def my_appointments():
    patient_id = session.get('patient_id')

    cursor = mysql.connection.cursor()

    cursor.execute("""
    SELECT a.appointment_id, a.appointment_date, a.appointment_time,
           a.status,
           CONCAT(d.firstname, ' ', d.lastname) AS doctor_name
    FROM appointments a
    JOIN doctors d ON a.doctor_id = d.doctor_id
    WHERE a.patient_id = %s
    ORDER BY a.appointment_date DESC, a.appointment_time DESC
""", (patient_id,))

    appointments = cursor.fetchall()
    cursor.close()

    return render_template("my_appointments.html", appointments=appointments)



# Route To Update Appointment
@patient.route('/reschedule/<int:id>', methods=['POST'])
def update_reschedule(id):
    new_date = request.form.get('appointment_date')
    new_time = request.form.get('appointment_time')

    cursor = mysql.connection.cursor()

    cursor.execute("""
        UPDATE appointments
        SET appointment_date = %s,
            appointment_time = %s,
            status = 'Scheduled'
        WHERE appointment_id = %s
    """, (new_date, new_time, id))

    mysql.connection.commit()
    cursor.close()

    flash("Appointment rescheduled successfully!", "success")

    return redirect(url_for('patient.my_appointments'))



# Route To Cancel Appointment
@patient.route('/cancel_appointment/<int:id>')
def cancel_appointment(id):
    cursor = mysql.connection.cursor()

    cursor.execute("""
        UPDATE appointments
        SET status = 'Cancelled'
        WHERE appointment_id = %s
    """, (id,))

    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('patient.my_appointments'))


# Patient Logout Route
@patient.route('/logout')
def patient_logout():
    # Clear the session
    session.clear()
    # Redirect to login page
    return redirect(url_for('loginroles.universal_login'))


