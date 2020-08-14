from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f"User {self.username}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Cat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(400))
    age = db.Column(db.Integer)
    period = db.Column(db.String(16))
    sex = db.Column(db.String(32))
    fur = db.Column(db.String(32))
    when_came = db.Column(db.String(32))
    picture = db.Column(db.String(64))
    googlePhoto1 = db.Column(db.String(256))
    googlePhoto2 = db.Column(db.String(256))
    googlePhoto3 = db.Column(db.String(256))
    isActive = db.Column(db.Boolean, unique=False, default=True)
    isYoung = db.Column(db.Boolean, unique=False, default=False)
    readyToBeAdopted = db.Column(db.Boolean, unique=False, default=False)
    currentlyOnMeds = db.Column(db.Boolean, unique=False, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return f"<Cat {self.name}"

@login.user_loader
def load_user(id):
    return User.query.get(int(id))