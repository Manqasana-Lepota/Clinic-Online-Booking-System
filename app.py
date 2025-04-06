from app import app
from app.adminViews import admin  # Import the blueprint
from app.doctorViews import doctor


# Register the admin blueprint
app.register_blueprint(admin, url_prefix="/admin")

# Register the blueprint
app.register_blueprint(doctor)





    
if __name__ == "__main__":
    app.run(debug=True)
        

        
