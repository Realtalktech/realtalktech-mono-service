from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from . import db

# models/post_discuss_category.py
class PostDiscussCategory(db.Model):
    __tablename__ = 'PostDiscussCategory'
    post_id = db.Column(db.Integer, db.ForeignKey('Post.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('DiscussCategory.id'), primary_key=True)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)