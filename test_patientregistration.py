import unittest
from flask import Flask
from app import app  # Replace 'your_app' with the name of your Flask app
from flask_testing import TestCase

class TestPatientRegistrationForm(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

def test_successful_registration(self):
        response = self.client.post('/patientregistration_form', data={
            'firstname': 'John',
            'lastname': 'Doe',
            'email': 'john@example.com',
            'password': 'secure_password',
            'contact': '1234567890',
            'address': '123 Main St'
        })
        self.assertIn(b'Patient Registered Successful !', response.data)

if __name__ == '__main__':
    unittest.main()