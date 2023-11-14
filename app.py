from app import app

    
"""from flask import Flask, request, session, redirect, url_for, render_template
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = "Thisismysecretket"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'OnlineBookings_DB'
mysql = MySQL(app)


# For automatic template reload
app.config['TEMPLATES_AUTO-RELOAD'] = True

@app.route('/')
# Choose user type
@app.route('/loginroles')
def loginroles():
    return render_template("loginroles.html")



# Admin Login Page
@app.route('/adminlogin_page', methods=['GET', 'POST'])
def adminlogin_page():
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
            return redirect(url_for('admindashboard'))
        else:
            message ='Login failed. Please check your credentials.', 'danger'
    return render_template("adminlogin_page.html", message = message)



# Admin dashboard
@app.route('/adminDashboard')
def admindashboard():
    return render_template("admindashboard.html")


@app.route('/doctors', methods = ['GET'])
def doctors():
    return render_template("doctors.html")

@app.route('/addNewDoctor', methods = ['GET', 'POST'])
def addNewDoctor():
    return render_template("addNewDoctor.html")





@app.route('/patientlogin_page', methods = ['GET', 'POST'])
def patientlogin_page():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM patient WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['patientid'] = user['patientid']
            session['firstname'] = user['firstname']
            session['lastname'] = user['lastname']
            session['email'] = user['email']
            session['contact'] = user['contact']
            session['address'] = user['address']
            message = 'Logged in successfully !'
            return redirect(url_for('patientdashboard'))
        else:
            message = 'Please enter correct email / password'
    return render_template("patientlogin_page.html", message = message)


@app.route('/patientregistration_form', methods = ['GET', 'POST'])
def patientregistration_form():
    message = ''
    if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'email' in request.form and 'password' in request.form and 'contact' in request.form and 'address'in request.form:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        contact = request.form['contact']
        address = request.form['address']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM patient WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            message = 'User already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address !'
        elif not firstname or not lastname or not password or not email or not contact or not address:
            message = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO patient (firstname, lastname, email, password, contact, address) VALUES (% s, % s, % s, % s, % s, % s)', (firstname, lastname, email, password, contact, address))
            mysql.connection.commit()
            message = 'Patient Registered Successful !'
    elif request.method == 'POST':
        message = 'Please fill out the form !'
    return render_template("patientregistration_form.html", message = message)


@app.route('/patientdashboard', methods = ['GET'])
def patientdashboard():
    return render_template("patientdashboard.html")



@app.route('/patientinfo', methods = ['GET', 'POST'])
def patientinfo():
    if  'loggedin' in session:
        viewPatientId = request.args.get('patientid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM patient WHERE patientid = % s', (viewPatientId, ))
        user = cursor.fetchone()
        return render_template("patientinfo.html", user = user)
    return redirect(url_for('patientlogin_page'))


@app.route('/user_count', methods = ['GET'])
def get_user_count():
    cur = mysql.connection.cursor()
    cur.execute('SELECT COUNT(*) FROM patient')
    user_count = cur.fetchone()[0]
    cur.close()
    return render_template('user_count.html', user_count = user_count)"""



"""@app.route('/login', methods = ['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            if user['role'] == 'admin':
                session['loggedin'] = True
                session['userid'] = user['userid']
                session['name'] = user['name']
                message = 'Logged in successfully !'
                return redirect(url_for('users'))
            else:
                message = 'Only admin can login'
        else:
            message = 'Please enter correct email / password'
    return render_template('login.html', message = message)


@app.route('/logout')
def lgout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    session.pop('name', None)
    return redirect(url_for('login'))



@app.route('/users', methods = ['GET', "POST"])
def users():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user')
        users = cursor.fetchall()
        return render_template("users.html", users = users)
    return redirect(url_for('login'))



@app.route("/view", methods = ['GET', 'POST'])
def view():
    if  'loggedin' in session:
        viewUserId = request.args.get('userid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE userid = % s', (viewUserId, ))
        user = cursor.fetchone()
        return render_template("view.html", user = user)
    return redirect(url_for('login'))



@app.route("/password_change", methods = ['GET', 'POST'])
def password_change():
    message = ''
    if 'loggedin' in session:
        changePassUserId = request.args.get('userid')
        if request.method == 'POST' and 'password' in request.form and 'confirm_pass' in request.form and'userid' in request.form :
            password = request.form['password']
            confirm_pass = request.form['confirm_pass']
            userId = request.form['userid']
            if not password or not confirm_pass:
                message = 'Please fill out the form !'
            elif password != confirm_pass:
                message = 'Confirm pasword is not equal!'
            else:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('UPDATE user SET password =% s WHERE userid =% s', (password, (userId, )))
                mysql.connection.commit()
                message = 'Password updated !'
        elif request.method == 'POST':
            message = 'Please fill out the form !'
        return render_template("password_change.html", message = message, changePassUserId = changePassUserId)
    return redirect(url_for('login'))



@app.route("/delete", methods = ['GET'])
def delete():
    if 'loggedin' in session:
        deleteUserId = request.args.get('userid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM user WHERE userid = % s', (deleteUserId, ))
        mysql.connection.commit()
        return redirect(url_for('users'))
    return redirect(url_for('login'))


@app.route("/register", methods = ['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form and 'role' in request.form and 'country' in request.form:
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        country = request.form['country']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            message = 'User already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address !'
        elif not name or not password or not email:
            message = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user (name, email, password, role, country) VALUES (% s, % s, % s, % s, % s)', (name, email, password, role, country))
            mysql.connection.commit()
            message = 'New user created!'
    elif request.method == 'POST':
        message = 'Please fill out the form !'
    return render_template('register.html', message = message)


@app.route("/edit", methods = ['GET', 'POST'])
def edit():
    msg = ''
    if 'loggedin' in session:
        editUserId = request.args.get('userid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE userid = % s', (editUserId, ))
        editUser = cursor.fetchone()
        if request.method == 'POST' and 'name' in request.form and 'userid' in request.form and 'role' in request.form and 'country' in request.form:
            userName = request.form['name']
            role = request.form['role']
            country = request.form['country']
            userId = request.form['userid']
            if not re.match(r'[A_Za-z0-9]+', userName):
                msg = 'name must contain only characters and numbers !'
            else:
                cursor.execute('UPDATE user SET name =% s, role =% s, country =% s WHERE userid =% s', (userName, role, country, (userId, ), ))
                mysql.connection.commit()
                msg = 'User updated !'
                return redirect(url_for('users'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("edit.html", msg = msg, editUser = editUser)
    return redirect(url_for('login'))"""



if __name__ == "__main__":
    app.run(debug=True)
        

        
