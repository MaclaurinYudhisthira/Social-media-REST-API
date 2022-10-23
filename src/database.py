from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# DB Object
db = SQLAlchemy()

#DB Models
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(25),unique=True, nullable=False)
    email = db.Column(db.String(120),unique=True, nullable=False)
    password=db.Column(db.String(150), nullable=False)
    followers = db.Column(db.Integer, nullable=False)
    following = db.Column(db.Integer, nullable=False)
    def __init__(self,username,email,password):
        self.username = username
        self.email = email
        self.password = password
        self.followers = 0
        self.following = 0

class Follower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)
    def __init__(self,user_id,follower_id):
        self.user_id=user_id
        self.follower_id=follower_id

class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    created_time= db.Column(db.String(20),nullable=False)
    likes = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Integer, nullable=False)
    def __init__(self,user_id,title,description):
        self.user_id=user_id
        self.title=title
        self.description=description
        self.created_time=str(datetime.utcnow())[:19]
        self.likes = 0
        self.comments = 0

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'),nullable=False)
    def __init__(self,user_id,post_id):
        self.user_id=user_id
        self.post_id=post_id

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'),nullable=False)
    comment = db.Column(db.String(500), nullable=False)
    def __init__(self,user_id,post_id,comment):
        self.user_id=user_id
        self.post_id=post_id
        self.comment=comment