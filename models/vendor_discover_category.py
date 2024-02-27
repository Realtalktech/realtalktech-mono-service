from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from . import db

# models/vendor_discover_category.py
class VendorDiscoverCategory(db.Model):
    __tablename__ = 'VendorDiscoverCategory'
    vendor_id = db.Column(db.Integer, db.ForeignKey('DiscoverVendor.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('DiscoverCategory.id'), primary_key=True)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)