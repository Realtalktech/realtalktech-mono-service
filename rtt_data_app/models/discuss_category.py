from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from . import db

# models/discuss_category.py
class DiscussCategory(db.Model):
    __tablename__ = 'DiscussCategory'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    posts = db.relationship('Post', secondary='PostDiscussCategory', back_populates='categories')