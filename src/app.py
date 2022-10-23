from flask import Flask
import dotenv
import os
from flask_jwt_extended import JWTManager
from auth import auth
from database import db

# app object
app=Flask(__name__)

# loading .env
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

# secret key for session
app.secret_key=os.getenv("SECRET_KEY")

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

# database setup
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///social.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db.app = app
db.init_app(app)

# Creating Database
with app.app_context():
    db.create_all()

# Blueprint for URL Prefix
app.register_blueprint(auth, url_prefix="/api")

if __name__=="__main__":
    app.run(debug=True)