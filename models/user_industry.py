from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from . import db

class UserIndustry(db.Model):
    __tablename__ = 'UserIndustry'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    industry_id = db.Column(db.Integer, db.ForeignKey('Industry.id'), nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=backref('user_industries', lazy=True))
    industry = db.relationship('Industry', backref=backref('user_industries', lazy=True))