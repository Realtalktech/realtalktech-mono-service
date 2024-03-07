from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
from rtt_data_app.app import db
from rtt_data_app.models import Comment, CommentTag, CommentUpvote, User, Post
from rtt_data_app.auth import token_required
from rtt_data_app.utils.deprecated.responseFormatter import convert_keys_to_camel_case
from sqlalchemy import func, exc
from werkzeug.exceptions import BadRequest, InternalServerError, Unauthorized
import logging

comment_bp = Blueprint('comment_bp', __name__)
logger = logging.getLogger(__name__)

@comment_bp.route('/getCommentsForPost', methods=['GET'])
@token_required
def get_comments(user_id):
    data = request.json
    if not user_id:
        raise Unauthorized()

    post_id = data.get('postId')
    page = data.get('page', 1)
    count = data.get('count', 10)

    if not post_id:
        raise BadRequest("postId is required")
    try:
        post:Post = Post.query.filter_by(id=post_id).first()
        post.id
    except AttributeError:
        raise BadRequest("post does not exist!")

    # Query to fetch comments and their upvote/downvote counts, and user vote
    try:
        comments_query = db.session.query(
            Comment.id.label("Comment_id"),
            User.id.label("user_id"),
            User.username.label("User_username"),
            Comment.comment_text.label("Comment_comment_text"),
            Comment.creation_time.label("Comment_creation_time"),
            Comment.update_time.label("Comment_update_time"),
            func.coalesce(func.sum(func.cast(CommentUpvote.is_downvote == False, db.Integer)), 0).label('total_upvotes'),
            func.coalesce(func.sum(func.cast(CommentUpvote.is_downvote == True, db.Integer)), 0).label('total_downvotes'),
            (func.sum(db.case((CommentUpvote.user_id == user_id, CommentUpvote.is_downvote == False), else_=0)) > 0).label('user_upvote'),
            (func.sum(db.case((CommentUpvote.user_id == user_id, CommentUpvote.is_downvote == True), else_=0)) > 0).label('user_downvote')
        ).select_from(Comment).join(User, Comment.user_id == User.id).outerjoin(CommentUpvote, Comment.id == CommentUpvote.comment_id).filter(
            Comment.post_id == post_id
        ).group_by(
            Comment.id, User.id
        ).order_by(
            Comment.id.desc()
        ).limit(count).offset((page - 1) * count)

        # Prepare the comments for the response
        comments_list = []
        for comment in comments_query:
            # Convert SQLAlchemy result to dictionary
            comment_dict = {
                'id': comment.Comment_id,
                'username': comment.User_username,
                'commentText': comment.Comment_comment_text,
                'creationTime': comment.Comment_creation_time.isoformat(),
                'updateTime': comment.Comment_update_time.isoformat(),
                'totalUpvotes': comment.total_upvotes,
                'totalDownvotes': comment.total_downvotes,
                'userVote': comment.user_upvote
            }
            
            # Get tags associated with comment
            tagged_users = db.session.query(User.username).join(
                CommentTag, CommentTag.tagged_user_id == User.id
            ).filter(CommentTag.comment_id == comment.Comment_id).all()
            
            comment_dict['taggedUsernames'] = [tag.username for tag in tagged_users]
            
            # Convert keys from snake_case to camelCase if needed
            comments_list.append(convert_keys_to_camel_case(comment_dict))

        # Prepare metadata
        metadata = {
            'postId': post_id,
            'searcherUserId': user_id,
            'page': page,
            'count': count
        }

        return jsonify({"metadata": metadata, "comments": comments_list})
    
    except exc.SQLAlchemyError as e:
        logger.error(str(e))
        raise InternalServerError(str(e))


@comment_bp.route('/makeComment', methods=['POST'])
@token_required
def make_comment(user_id):
    if not user_id:
      raise Unauthorized()  # 401 Unauthorized

    data = request.json
    post_id = data.get('postId')
    tagged_user_names = data.get('taggedUsernames', [])
    comment_text = data.get('commentText')

    # Validate input
    if not (post_id and user_id and comment_text):
        logger.error("Missing required information to create comment")
        raise BadRequest("Missing required information to create comment")

    try:
        # Insert comment into the database
        new_comment = Comment(post_id=post_id, user_id=user_id, comment_text=comment_text)
        db.session.add(new_comment)
        db.session.flush()  # used to get the id of new_comment without committing transaction

        # Insert comment tags into database
        for username in tagged_user_names:
            tagged_user = User.query.filter_by(username=username).first()
            if tagged_user:  # Check if user exists
                new_tag = CommentTag(comment_id=new_comment.id, tagged_user_id=tagged_user.id)
                db.session.add(new_tag)

        db.session.commit()

    except exc.SQLAlchemyError as e: 
        db.session.rollback()
        raise InternalServerError(str(e))

    return jsonify({"message": "Comment added successfully", "comment_id": new_comment.id}), 201


@comment_bp.route('/upvoteComment', methods=['PUT'])
@token_required
def vote_comment(user_id):
    if not user_id:
        raise Unauthorized() # 401 Unauthorized
    
    data = request.json
    comment_id = data.get('commentId')
    is_downvote = data.get('isDownvote')

    if not comment_id:
        raise BadRequest("Comment ID is required")
    
    if is_downvote is None:
        raise BadRequest("Vote intention is required")
    
    try:
        # Check if the user has already voted this comment
        vote = CommentUpvote.query.filter_by(user_id=user_id, comment_id=comment_id).first()

        if vote:
            # If trying to perform the opposite action, remove the vote
            if (vote.is_downvote != is_downvote):
                db.session.delete(vote)
            # If attempting the same action, do nothing (vote remains)
        else:
            # Insert new vote
            new_vote = CommentUpvote(comment_id=comment_id, user_id=user_id, is_downvote=is_downvote)
            db.session.add(new_vote)

        db.session.commit()

        return jsonify({"message": "Vote updated successfully"}), 200
    
    except exc.SQLAlchemyError as e:
        logger.error(str(e))
        raise InternalServerError(str(e))

