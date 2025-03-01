from app import app
from app.adminViews import admin  # Import the blueprint

# Register the admin blueprint
app.register_blueprint(admin, url_prefix="/admin")





    
if __name__ == "__main__":
    app.run(debug=True)
        

        
