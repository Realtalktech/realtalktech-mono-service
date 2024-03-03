from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from . import db

# models/user_discuss_category.py
class UserDiscussCategory(db.Model):
    __tablename__ = 'UserDiscussCategory'
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('DiscussCategory.id'), primary_key=True)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='subscribed_discuss_categories')