from app import app, db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    password_hash = db.Column(db.String(400))
    token = db.Column(db.String(30))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.token = generate_password_hash(self.username)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(400))
    description = db.Column(db.String(2000))
    date_execution = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', foreign_keys=[author_id])
    performer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    performer = db.relationship('User', foreign_keys=[performer_id])
    priority = db.Column(db.Integer)
    execution_phase = db.Column(db.Integer)
    todo_or_not_todo = db.Column(db.Boolean)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
