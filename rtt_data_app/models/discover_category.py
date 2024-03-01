from datetime import datetime
from . import db

# models/discover_category.py
class DiscoverCategory(db.Model):
    __tablename__ = 'DiscoverCategory'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(255), unique=True, nullable=False)
    icon = db.Column(db.Text, nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)