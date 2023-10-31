from app import app
from flask import Flask, render_template, redirect, request, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re



app.secret_key = "Thisismysecretket"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'OnlineBookings_DB'
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
            return redirect(url_for('admin_dashboard'))
        else:
            message ='Login failed. Please check your credentials.', 'danger'
    return render_template("admin_login.html")


@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template("admin_dashboard.html")



@app.route('/add_doctors')
def add_doctors():
    return render_template("add_doctors.html")


@app.route('/addNew_doctor', methods = ['GET', 'POST'])
def addNew_doctor():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'contact' in request.form and 'specialities' in request.form and 'password' in request.form:
         name = request.form['name']
         email = request.form['email']
         contact = request.form['contact']
         specialities = request.form['specialities']
         password = request.form['password']
         cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cur.execute('SELECT * FROM doctor WHERE email = % s', (email,))
         account = cur.fetchone()
         if account:
              message = 'Doctor already exists !'
         elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
              message = 'Invalid email address !'
         else:
            cur.execute('INSERT INTO doctor (name, email, contact, specialities, password) VALUES (% s, % s, % s, % s, % s)', (name, email, contact, specialities, password))
            mysql.connection.commit()
            message = 'Doctor Successful Added !'
    elif request.method == 'POST':
         message = 'Please fill out the form !'   
    return render_template("addNew_doctor.html", message=message)








@app.route('/view_doctor')
def view_doctor():
    return render_template("view_doctor.html")