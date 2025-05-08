from datetime import datetime
from app import db

class Therapy(db.Model):
    __tablename__ = 'therapy'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    therapy_type = db.Column(db.String(64), nullable=False)
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