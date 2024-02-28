# utils/post.py
from typing import List
from rtt_data_app.app import db
from rtt_data_app.models import Post as PostModel
from rtt_data_app.models import PostDiscoverVendor, PostDiscussCategory, DiscussCategory, DiscoverVendor, PostUpvote
from sqlalchemy import exc, func
from werkzeug.exceptions import InternalServerError, BadRequest
import logging
logger = logging.getLogger(__name__)

class Post:
    def __init__(self):
        pass

    def toggle_post_vote(self, post_id:int, user_id:int, is_downvote:bool) -> None:
        # Start a transaction
        try:
            # Attempt to find an existing vote
            vote = PostUpvote.query.filter_by(post_id=post_id, user_id=user_id).first()
            if vote:
                # If an existing vote is found, remove it if it's different from the new vote
                if vote.is_downvote != is_downvote:
                    db.session.delete(vote)
            else:
                # If no existing vote, create a new one
                new_vote = PostUpvote(post_id=post_id, user_id=user_id, is_downvote=is_downvote)
                db.session.add(new_vote)
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            logger.error(str(e))
            raise InternalServerError(f"Database error: {str(e)}")
        finally:
            db.session.commit()

    def create_post_and_fetch_id(
            self,
            author_id:int,
            title:str,
            body:str,
            category_ids:List[int],
            is_anonymous:bool,
            tagged_vendor_ids:List[int]
    )->int:
        try:
            # Create and insert post into database
            new_post = PostModel(user_id=author_id, title=title, body=body, is_anonymous=is_anonymous)
            db.session.add(new_post)
            db.session.flush()  # This is to get the post_id without committing the transaction

            # Link post to categories
            for category_id in category_ids:
                new_post_category = PostDiscussCategory(post_id=new_post.id, category_id=category_id)
                db.session.add(new_post_category)
            
            # Link post to vendors
            for tagged_vendor_id in tagged_vendor_ids:
                new_post_vendor = PostDiscoverVendor(post_id=new_post.id, vendor_id=tagged_vendor_id)
                db.session.add(new_post_vendor)
            
            db.session.commit()  # Commit all changes
            return new_post.id  # Return the ID of the new post
                
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            logger.error(str(e))
            raise InternalServerError(f"Database error: {str(e)}")
        
    def edit_post(self, author_id, post_id, new_title=None, new_body=None, new_category_ids=None, new_vendor_ids=None):
        try:
            post = PostModel.query.filter_by(id=post_id, user_id=author_id).first()
            if not post:
                raise BadRequest("Post not found or you do not have permission to edit this post")

            if new_title:
                post.title = new_title
            
            if new_body:
                post.body = new_body
            
            post.update_time = func.now()

            # Update categories
            if new_category_ids is not None:
                post.categories = DiscussCategory.query.filter(DiscussCategory.id.in_(new_category_ids)).all()

            # Update vendors
            if new_vendor_ids is not None:
                post.vendors = DiscoverVendor.query.filter(DiscoverVendor.id.in_(new_vendor_ids)).all()

            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            logger.error(str(e))
            raise InternalServerError(str(e))