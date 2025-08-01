from flask import Blueprint, render_template, redirect, request, url_for, session, flash, current_app
from app import mysql
import MySQLdb.cursors
import re
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

patient = Blueprint('patient', __name__)

@patient.route('/PatientDashboard')
def PatientDashboard():
    if 'username' not in session:
        return redirect(url_for('loginroles.universal_login'))

    firstname = session.get('firstname', 'Patient')
    return render_template("PatientDashboard.html", firstname=firstname)
   
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
            filepath = os.path.join(upload_folder, filename)
            profile_image.save(filepath)

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
                return redirect(url_for('patient.PatientDashboard'))

    return render_template("PatientsRegisterForm.html", message=message)
