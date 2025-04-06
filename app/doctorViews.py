from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors  # Import MySQLdb cursors
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = "Thisismysecretkey"  # Change this to a secure secret key

# MySQL Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "BookingSystem"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"


mysql = MySQL(app)

# Define Blueprint for Doctor
doctor = Blueprint('doctor', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# You can set the upload folder path as follows:
UPLOAD_FOLDER = 'static/images'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images')




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
            session['specialization'] = doctor['specialization']  # Ensure specialization is saved here
 
            flash("Login successful!", "success")
            return redirect(url_for('doctor.DoctorDashboard'))
        else:
            flash("Invalid credentials, please try again.", "danger")

        cursor.close()

    return render_template('DoctorLogin.html')


@doctor.route('/doctor-dashboard', endpoint="DoctorDashboard")
def DoctorDashboard():
    if 'doctor_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('doctor.DoctorLogin'))

    # Retrieve doctor details from the session
    doctor = {
        'firstname': session.get('firstname'),
        'lastname': session.get('lastname'),
        'profile_picture': session.get('profile_picture', 'default.jpeg'),
        'specialization': session.get('specialization')  # Optional specialization
    }

    return render_template('DoctorDashboard.html', doctor=doctor)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@doctor.route('/upload-profile-picture', methods=['POST'])
def upload_profile_picture():
    if 'doctor_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('doctor.DoctorLogin'))

    if 'profile_picture' in request.files:
        file = request.files['profile_picture']

        if file.filename == '':
            flash("No file selected.", "danger")
            return redirect(url_for('doctor.DoctorDashboard'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Save the file name to session
            session['profile_picture'] = filename

            flash("Profile picture updated successfully!", "success")
            return redirect(url_for('doctor.DoctorDashboard'))

    flash("Invalid file type.", "danger")
    return redirect(url_for('doctor.DoctorDashboard'))


# Register the Blueprint
app.register_blueprint(doctor)

if __name__ == '__main__':
    app.run(debug=True)
