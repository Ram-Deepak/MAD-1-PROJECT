import os 
# from flask_security import uia_username_mapper
basedir = os.path.abspath(os.path.dirname(__file__))

# __file__ -> gives the path of the current file
# os.path.dirname(path) -> gives the directory name of the current file
# os.path.abspath(path) -> gives the abspath of the given path

class Config():
    DEBUG = False 
    SQLITE_DB_DIR = None 
    SQLALCHEMY_DATABASE_URI = None 
    SQLALCHEMY_TRACK_MODIFICATIONS = False 

class LocalDevelopmentConfig(Config):
    DEBUG = True # Allows flask to debug the code...Since this is development config we allow debugging
    SQLITE_DB_DIR = os.path.join(basedir, '../db_directory')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(SQLITE_DB_DIR, 'bloglitedb.sqlite3')
    SECRET_KEY ='dafi394rfi094m3f094rmdm93034u33jf9j'
    SECURITY_REGISTERABLE = True # Default value is False
    # # Tells if a user can register him/herself
    SECURITY_SEND_REGISTER_EMAIL = False  # Default value is True
    # # Tells if a mail must be sent after every new registratiion
    UPLOAD_FOLDER = "/home/ram/Desktop/IIT-M/PROJECT/21f2001114/MAD-1-PROJECT/upload_image"