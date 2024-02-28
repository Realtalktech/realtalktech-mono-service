from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from . import db

class UserInterestArea(db.Model):
    __tablename__ = 'UserInterestArea'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    interest_area_id = db.Column(db.Integer, db.ForeignKey('InterestArea.id'), nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=backref('user_interest_areas', lazy=True))
    interest_area = db.relationship('InterestArea', backref=backref('user_interest_areas', lazy=True))