from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from . import db

# models/user_public_vendor.py
class UserPublicVendor(db.Model):
    __tablename__ = 'UserPublicVendor'
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('PublicVendor.id'), primary_key=True, nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)