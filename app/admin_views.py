from app import app
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import logging



app.secret_key = "Thisismysecretket"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'OnlineBookings_DB'
app.config['MYSQL_AUTOCOMMIT'] = True
app.config['MYSQL_DATABASE_POOL_SIZE'] = 10  # Adjust as neede
mysql = MySQL(app)


@app.route('/admin_login', methods = ['GET', "POST"])
def admin_login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['username'] = username
            message = 'Login successful!', 'success'
            return redirect(url_for('Admin_Dashboard_Page'))
        else:
            message ='Login failed. Please check your credentials.', 'danger'
    return render_template("admin_login.html")


@app.route('/Admin_Dashboard_Page')
def Admin_Dashboard_Page():
    return render_template("Admin_Dashboard_Page.html")


# Fetching all doctors information from database    
@app.route('/Admin_Doctors_Page')
def Admin_Doctors_Page():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM doctors")
        data = cur.fetchall()
        return render_template("Admin_Doctors_Page.html", data=data)
    except Exception as e:
        print(f"Error: {e}")
        flash("An error occurred while fetching data from the database.", 'error')
        return render_template("Admin_Doctors_Page.html", data=None)
    finally:
        # Ensure that the database connection is closed in all cases
        if cur:
            cur.close()
    

# Inserting Doctor Data to the database
@app.route('/Admin_Insert_Doctor', methods = ['POST'])
def Admin_Insert_Doctor():
     if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'contact' in request.form and 'specialities' in request.form and 'password' in request.form:
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        specialities = request.form['specialities']
        password = request.form['password']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM doctors WHERE email = % s', (email,))
        account = cur.fetchone()
        if account:
              flash('Doctor already exists !', 'warning')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
             flash('Invalid email address !', 'error')
        elif not name or not email or not contact or not specialities or not password:
             flash('Please fill out the form !', 'warning')
        else:
             cur.execute("INSERT INTO doctors (name, email, contact, specialities, password) VALUES (%s, %s, %s, %s, %s)", (name, email, contact, specialities, password))
             mysql.connection.commit()
             flash('New Doctor Successfully Added !', 'success')
        return redirect(url_for('Admin_Doctors_Page'))
     return 'Invalid request method'
     



@app.route('/Admin_Patients_Page')
def Admin_Patients_Page():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM patient")
        data = cur.fetchall()
        return render_template("Admin_Patients_Page.html", patient=data)
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred."
    finally:
        if cur:
            cur.close()
















@app.route('/admin_patientslist')
def admin_patientslist():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM patient")
    data = cur.fetchall()
    cur.close()
    return render_template("admin_patientslist.html", patient = data)










@app.route('/view_doctor')
def view_doctor():
    return render_template("view_doctor.html")
