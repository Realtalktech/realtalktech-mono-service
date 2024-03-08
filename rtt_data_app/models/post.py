from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from . import db

class Post(db.Model):
    __tablename__ = 'Post'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    is_anonymous = db.Column(db.Boolean, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    votes = db.relationship('PostUpvote', back_populates='post')
    user = db.relationship('User', backref=backref('posts', lazy=True))
    categories = db.relationship('DiscussCategory', secondary='PostDiscussCategory', back_populates='posts')
    vendors = db.relationship('DiscoverVendor', secondary='PostDiscoverVendor', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post')