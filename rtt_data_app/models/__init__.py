# models/__init__.py
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from .comment_tag import CommentTag
from .comment_upvote import CommentUpvote
from .comment import Comment
from .discover_category import DiscoverCategory
from .discover_vendor import DiscoverVendor
from .discuss_category import DiscussCategory
from .industry import Industry
from .interest_area import InterestArea
from .post_discover_vendor import PostDiscoverVendor
from .post_discuss_category import PostDiscussCategory
from .post_upvote import PostUpvote
from .post import Post
from .public_vendor import PublicVendor
from .user_discuss_category import UserDiscussCategory
from .user_industry import UserIndustry
from .user_interest_area import UserInterestArea
from .user_public_vendor import UserPublicVendor
from .user_public_vendor_endorsement import UserPublicVendorEndorsement
from .user import User
from .vendor_discover_category import VendorDiscoverCategory
