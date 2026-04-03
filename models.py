from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# User Table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    # Relationship with Resume table
    resumes = db.relationship('Resume', backref='user', lazy=True)

# Resume Table
class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer)
    detected_skills = db.Column(db.Text)  # Stored as comma-separated string or JSON
    missing_skills = db.Column(db.Text)   # Stored as comma-separated string or JSON
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)