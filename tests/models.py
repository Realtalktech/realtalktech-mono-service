# models.py
from app import db 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255))
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    creation_time = db.Column(db.DateTime(3), server_default=db.func.current_timestamp(3))
    update_time = db.Column(db.DateTime(3), server_default=db.func.current_timestamp(3))
    # Add relationships and other fields...

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    creation_time = db.Column(db.DateTime(3), server_default=db.func.current_timestamp(3))
    update_time = db.Column(db.DateTime(3), server_default=db.func.current_timestamp(3))
    # Add relationships and other fields...

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    creation_time = db.Column(db.DateTime(3), server_default=db.func.current_timestamp(3))
    update_time = db.Column(db.DateTime(3), server_default=db.func.current_timestamp(3))
    # Add relationships and other fields...


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    creation_time = db.Column(db.DateTime(3), server_default=db.func.current_timestamp(3))
    update_time = db.Column(db.DateTime(3), server_default=db.func.current_timestamp(3))
    # Relationships and other fields...


