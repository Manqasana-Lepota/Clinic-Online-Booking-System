from flask import Flask

app = Flask(__name__)

from app import home_views
from app import loginroles_views
from app import adminViews
from app import patient_views