from application.database import db
from flask_login import UserMixin
import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(), nullable=False)
    lastname = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False, unique=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    profile = db.relationship('Profile', backref='User', lazy=True, uselist=False)
    posts = db.relationship('Posts', backref='User', lazy='dynamic')

    def __init__(self,fname,lname,email,username,password):
        self.firstname = fname
        self.lastname = lname 
        self.email = email 
        self.username = username 
        self.password = password

class Profile(db.Model):
    __tablename__ = 'profile'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'),nullable=False, unique=True)
    posts = db.Column(db.Integer(), nullable=True)
    followers = db.Column(db.Integer(), nullable=True)
    following = db.Column(db.Integer(), nullable=True)
    photo = db.Column(db.LargeBinary(), nullable=True)

    def __init__(self, user_id, post_count, followers_count, following_count, photo):
        self.user_id = user_id
        self.posts = post_count
        self.followers = followers_count
        self.following = following_count
        self.photo = photo

class Followers(db.Model):
    __tablename__ = 'followers'
    f_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer(), nullable=False)
    follower_id = db.Column(db.Integer())

    def __init__(self, user_id, follower_id):
        self.user_id = user_id 
        self.follower_id = follower_id

class Following(db.Model):
    __tablename__ = 'following'
    fl_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer(), nullable=False)
    following_id = db.Column(db.Integer())

    def __init__(self, user_id, following_id):
        self.user_id = user_id
        self.following_id = following_id

class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=False)
    created = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow)
    image = db.Column(db.LargeBinary(), nullable=False)

    def __init__(self,user_id,title,description,image):
        self.user_id=user_id
        self.title=title
        self.description=description
        self.image=image