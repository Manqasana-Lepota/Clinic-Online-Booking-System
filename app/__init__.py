import os
from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()

def create_app():
    app = Flask(__name__)

    app.secret_key = "Thisismysecretkey"

    # MySQL config
    app.config["MYSQL_HOST"] = "localhost"
    app.config["MYSQL_USER"] = "root"
    app.config["MYSQL_PASSWORD"] = "password"
    app.config["MYSQL_DB"] = "BookingSystem"
    app.config["MYSQL_CURSORCLASS"] = "DictCursor"
    app.config['UPLOAD_FOLDER'] = 'static/uploads' 

    # Init extensions
    mysql.init_app(app)

    # Register blueprints
    from app.homeViews import home
    from app.loginrolesViews import loginroles
    from app.adminViews import admin
    from app.patientViews import patient
    from app.doctorViews import doctor

    app.register_blueprint(home)
    app.register_blueprint(loginroles)
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(patient, url_prefix="/patient")
    app.register_blueprint(doctor, url_prefix="/doctor")

    return app


