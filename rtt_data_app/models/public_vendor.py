from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from . import db

# models/public_vendor.py
class PublicVendor(db.Model):
    __tablename__ = 'PublicVendor'
    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(255), unique=True, nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vendor_user_associations = db.relationship('UserPublicVendor', back_populates='vendor')
    # Relationship for endorsements
    endorsements = db.relationship('UserPublicVendorEndorsement', back_populates='vendor')