from app import app, db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

meta_tags_task_table = db.Table('tags_task',
                                db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
                                db.Column('meta_tag_task_id', db.Integer, db.ForeignKey('meta_tags_task.id'))
                                )


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
    author = db.relationship('User', foreign_keys=[author_id], backref=db.backref('author_tasks', lazy=True))
    performer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    performer = db.relationship('User', foreign_keys=[performer_id], backref=db.backref('performer_tasks', lazy=True))
    category = db.Column(db.String(100))
    priority = db.Column(db.Integer)
    execution_phase = db.Column(db.Integer)
    meta_tags = db.relationship('MetaTagsTask', secondary=meta_tags_task_table,
                                backref=db.backref('tasks', lazy='dynamic'))
    todo_or_not_todo = db.Column(db.Boolean)


class MetaTagsTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(256))


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
