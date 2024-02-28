from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from . import db

# models/discover_vendor.py
class DiscoverVendor(db.Model):
    __tablename__ = 'DiscoverVendor'
    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(255), unique=True, nullable=False)
    vendor_type = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    vendor_hq = db.Column(db.String(255))
    total_employees = db.Column(db.Integer)
    vendor_homepage_url = db.Column(db.String(255))
    vendor_logo_url = db.Column(db.String(255))
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    posts = db.relationship('Post', secondary='PostDiscoverVendor', back_populates='vendors')