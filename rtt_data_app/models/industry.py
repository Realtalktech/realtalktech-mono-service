from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from . import db

# models/industry.py
class Industry(db.Model):
    __tablename__ = 'Industry'
    id = db.Column(db.Integer, primary_key=True)
    industry_name = db.Column(db.String(255), unique=True, nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)