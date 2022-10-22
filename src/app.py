from flask import Flask,jsonify,request
import dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import JWTManager,jwt_required, create_access_token, create_refresh_token, get_jwt_identity

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

# DB Object
db = SQLAlchemy(app)

#DB Models
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120),unique=True, nullable=False)
    password=db.Column(db.String(150), nullable=False)
    def __init__(self,email,password):
        self.email = email
        self.password = password

class Follower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'),nullable=False)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.user_id'),nullable=False)
    def __init__(self,user_id,follower_id):
        self.user_id=user_id
        self.follower_id=follower_id

# Creating Database
with app.app_context():
    db.create_all()

# URL Profix
class PrefixMiddleware(object):

    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):

        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return jsonify({"message":"This url does not belong to the app"}),404 # URL not found 404

app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/api')

# Routes
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message":"Hey! This is my API"}),200 # 200 OK

# Route for login and genrate jwt token
@app.route("/authenticate", methods=["POST"])
def authenticate():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=email).first()
    print(user)
    if user:
        
        is_pass_correct = check_password_hash(user.password, password)

        if is_pass_correct:
            refresh = create_refresh_token(identity=user.user_id)
            access = create_access_token(identity=user.user_id)

            return jsonify({
                'user': {
                    'refresh': refresh,
                    'access': access,
                    'email': user.email
                }

            }), 200 # 200 OK

    return jsonify({'error': 'Wrong credentials'}), 401 # 401 unathourized

# Route for login and genrate jwt token
@app.route("/follow/<id>", methods=["POST"])
def follow(id):
    

# Route to create data for testing
@app.route("/tdata", methods=["GET"])
def tdata():
    password='123'
    pwd_hash = generate_password_hash(password)
    user = User(email="test@app.com", password=pwd_hash)
    db.session.add(user)
    for i in range(10):
        user = User(email=f"test{i}@app.com", password=pwd_hash)
        db.session.add(user)
    db.session.commit()

    return jsonify({'message': "Test data created"}), 201 # 201 Created



if __name__=="__main__":
    app.run(debug=True)