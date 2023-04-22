from flask import Flask, request, render_template
from application.config import LocalDevelopmentConfig
from application.database import db
from application.models import User

app = None 

#function to create an app instance
def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(LocalDevelopmentConfig) # Configurations written in config.py file seperately
    db.init_app(app) 
    app.app_context().push()
    return app

app = create_app()

# Import all the controllers so they are loaded
from application.controllers import *

# This is a flask error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404 # Whenever there is a 404 error, app will redirect to 404 page

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__=='__main__':  # Point where the app starts runnning
    app.run(host='0.0.0.0',port=8000)