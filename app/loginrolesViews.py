from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import mysql

loginroles = Blueprint('loginroles', __name__)

@loginroles.route('/login', methods=['GET', 'POST'])
def login():
    # login logic here
    return render_template('loginroles.html')