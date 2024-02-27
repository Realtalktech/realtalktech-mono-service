# models/__init__.py
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from .user import User
from .post import Post
from .user_industry import UserIndustry
from .user_interest_area import UserInterestArea
