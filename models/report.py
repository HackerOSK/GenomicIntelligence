from datetime import datetime
from app import db

class Report(db.Model):
    __tablename__ = 'report'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report_name = db.Column(db.String(128), nullable=False)
    report_type = db.Column(db.String(64), nullable=False)
    report_text = db.Column(db.Text, nullable=False)
    extracted_data = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    therapies = db.relationship('Therapy', backref='report', lazy=True)