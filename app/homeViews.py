from flask import Blueprint, render_template

home = Blueprint('home', __name__)

@home.route('/')
def homePage():
    return render_template('home.html')


