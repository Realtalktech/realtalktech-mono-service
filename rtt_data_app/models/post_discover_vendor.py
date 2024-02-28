from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from . import db

class PostDiscoverVendor(db.Model):
    __tablename__ = 'PostDiscoverVendor'

    post_id = db.Column(db.Integer, db.ForeignKey('Post.id'), primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('DiscoverVendor.id'), primary_key=True)
    creation_time = db.Column(db.DateTime(3), server_default=db.func.current_timestamp())
    update_time = db.Column(db.DateTime(3), server_default=db.func.current_timestamp())