from datetime import datetime
from extensions import db

class Therapy(db.Model):
    __tablename__ = 'therapy'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    approach = db.Column(db.String(50))  # Allopathy, Homeopathy, Ayurveda
    efficacy_score = db.Column(db.Float)
    safety_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
