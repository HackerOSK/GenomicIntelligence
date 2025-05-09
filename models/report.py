from datetime import datetime
from extensions import db

class Report(db.Model):
    __tablename__ = 'report'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    extracted_entities = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    therapies = db.relationship('Therapy', backref='report', lazy=True)
