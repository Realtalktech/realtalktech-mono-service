from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from . import db

class CommentUpvote(db.Model):
    __tablename__ = 'CommentUpvote'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('Comment.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    is_downvote = db.Column(db.Boolean, nullable=False)
    creation_time = db.Column(db.DateTime(3), server_default=db.func.current_timestamp())
    update_time = db.Column(db.DateTime(3), server_default=db.func.current_timestamp())

    comment = db.relationship('Comment', back_populates='upvotes')
    user = db.relationship('User', backref='upvotes')