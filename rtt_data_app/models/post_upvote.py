from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from . import db

class PostUpvote(db.Model):
    __tablename__ = 'PostUpvote'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_downvote = db.Column(db.Boolean, nullable=False)
    creation_time = db.Column(db.DateTime(3), server_default=db.func.current_timestamp())
    update_time = db.Column(db.DateTime(3), server_default=db.func.current_timestamp())