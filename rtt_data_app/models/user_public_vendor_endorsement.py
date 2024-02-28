from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from . import db

# models/user_public_vendor_endorsement.py
class UserPublicVendorEndorsement(db.Model):
    __tablename__ = 'UserPublicVendorEndorsement'
    id = db.Column(db.Integer, primary_key=True)
    endorser_user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    endorsee_user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    vendor_id = db.Column(db.Integer, db.ForeignKey('PublicVendor.id'))
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    endorser = db.relationship('User', foreign_keys=[endorser_user_id], backref='given_endorsements')
    endorsee = db.relationship('User', foreign_keys=[endorsee_user_id], backref='received_endorsements')
    vendor = db.relationship('PublicVendor', back_populates='endorsements')