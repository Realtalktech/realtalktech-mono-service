from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
from rtt_data_app.app import db
from rtt_data_app.models import Comment, CommentTag, CommentUpvote, User
from rtt_data_app.utils import DBManager
from rtt_data_app.auth import token_required
from rtt_data_app.utils.deprecated.responseFormatter import convert_keys_to_camel_case
from sqlalchemy import func, exc
from werkzeug.exceptions import BadRequest

comment_bp = Blueprint('comment_bp', __name__)
db_manager = DBManager()

@comment_bp.route('/getCommentsForPost', methods=['GET'])
@token_required
def get_comments(user_id):
    data = request.json
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401  # 401 Unauthorized
    post_id = data.get('postId')
    page = data.get('page', 1)
    count = data.get('count', 10)

    if not post_id:
        raise BadRequest("postId is required")

    # Query to fetch comments and their upvote/downvote counts, and user vote
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


@comment_bp.route('/makeComment', methods=['POST'])
@token_required
def make_comment(user_id):
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401  # 401 Unauthorized
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    try:
        data = request.json
        post_id = data.get('postId')
        tagged_user_names = data.get('taggedUsernames', [])
        comment_text = data.get('commentText')

        # Validate input
        if not (post_id and user_id and comment_text):
            return jsonify({"error": "Missing required comment information"}), 400

        # Insert comment into the database
        cursor.execute("""
            INSERT INTO Comment (post_id, user_id, comment_text)
            VALUES (%s, %s, %s)
        """, (post_id, user_id, comment_text))
        comment_id = cursor.lastrowid

        # Insert comment tags into database
        for username in tagged_user_names:
            # Get tagged_user_id
            cursor.execute("""SELECT id FROM User WHERE username = %s""", (username))
            tagged_user_id = cursor.fetchone()['id']
            cursor.execute("INSERT INTO CommentTag (comment_id, tagged_user_id) VALUES (%s , %s)", (comment_id, tagged_user_id))

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Comment added successfully", "comment_id": comment_id}), 201


@comment_bp.route('/upvoteComment', methods=['PUT'])
@token_required
def vote_comment(user_id):
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401  # 401 Unauthorized
    
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    try:
        data = request.json
        comment_id = data.get('commentId')
        is_downvote = data.get('isDownvote', False)  # Default to False for upvote, True for downvote

        if not comment_id:
            return jsonify({"error": "Comment ID is required"}), 400

        # Check if the user has already voted this comment
        cursor.execute("""
            SELECT id, is_downvote FROM CommentUpvote 
            WHERE user_id = %s AND comment_id = %s
        """, (user_id, comment_id))
        vote = cursor.fetchone()

        if vote:
            # If trying to perform the opposite action, remove the vote
            if (vote['is_downvote'] and not is_downvote) or (not vote['is_downvote'] and is_downvote):
                cursor.execute("""
                    DELETE FROM CommentUpvote 
                    WHERE id = %s
                """, (vote['id'],))
            # If attempting the same action, do nothing (vote remains)
        else:
            # Insert new vote
            cursor.execute("""
                INSERT INTO CommentUpvote (comment_id, user_id, is_downvote)
                VALUES (%s, %s, %s)
            """, (comment_id, user_id, is_downvote))

        conn.commit()

    except Exception as e:  # Using a generic exception to catch all possible errors
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Vote updated successfully"}), 200