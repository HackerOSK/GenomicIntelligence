from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    profiles = db.relationship('Profile', backref='user', lazy=True)
    reports = db.relationship('Report', backref='user', lazy=True)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(16))
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    lifestyle = db.Column(db.String(64))
    medical_history = db.Column(db.Text)
    allergies = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report_name = db.Column(db.String(128), nullable=False)
    report_type = db.Column(db.String(64), nullable=False)
    report_text = db.Column(db.Text, nullable=False)
    extracted_data = db.Column(db.Text)  # JSON string of extracted entities
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    therapies = db.relationship('Therapy', backref='report', lazy=True)

class Therapy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    therapy_type = db.Column(db.String(64), nullable=False)  # allopathy, homeopathy
    therapy_name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    efficacy_score = db.Column(db.Float)
    compatibility_score = db.Column(db.Float)
    safety_score = db.Column(db.Float)
    cost_score = db.Column(db.Float)
    overall_score = db.Column(db.Float)
    side_effects = db.Column(db.Text)
    contraindications = db.Column(db.Text)
    supporting_evidence = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
