from app import app
from flask import render_template

@app.route('/loginroles')
def loginroles():
    return render_template("loginroles.html")