from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
from utils import DBManager, token_required
from models import Post

post_bp = Blueprint('post_bp', __name__)
db_manager = DBManager()


@post_bp.route('/makePost', methods=['POST'])
@token_required
def make_post(user_id):
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401  # 401 Unauthorized

    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    try:
        data = request.json
        title = data.get('title')
        body = data.get('body')
        categories = data.get('categories', [])  # List of category names
        is_anonymous = data.get('isAnonymous')
        vendors = data.get('vendors', []) # List of vendor names

        if not (title and body) or (is_anonymous is None):
            missing_fields = ''
            if not title: missing_fields += 'title '
            if not body: missing_fields += 'body '
            if is_anonymous is None: missing_fields += 'anonymity status '
            return jsonify({"error": f"Missing required post information: {missing_fields}"}), 400

        post = Post(
            author_id=user_id,
            title=title,
            body=body,
            category_names=categories,
            is_anonymous=is_anonymous,
            tagged_vendor_names=vendors
        )
        post.create_post(cursor)
        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Post created successfully", "post_id": post.post_id}), 201

@post_bp.route('/editPost', methods=['PUT'])
@token_required
def edit_post(user_id):
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401  # 401 Unauthorized
    try:
        data = request.json
        post_id = data.get('postId')
        new_title = data.get('title')
        new_body = data.get('body')
        new_categories = set(data.get('categories', []))  # List of new category names
        new_vendors = set(data.get('vendors', [])) # List of new vendor names

        if not post_id:
            return jsonify({"error": "Post ID is required"}), 400
        
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        
        post = Post.post_from_post_id(cursor, post_id)

        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        post.edit_post(
            cursor, new_title, new_body, new_categories, new_vendors
        )

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Post updated successfully"}), 200

@post_bp.route('/upvotePost', methods=['PUT'])
@token_required
def vote_post(user_id):
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401  # 401 Unauthorized
    try:
        data = request.json
        post_id = data.get('postId')
        is_downvote = data.get('isDownvote', False)  # False for upvote, True for downvote

        if not post_id:
            return jsonify({"error": "Post ID is required"}), 400

        conn = db_manager.get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        vote = Post.get_user_vote_on_post(cursor, user_id, post_id)

        if vote:
            if (vote['is_downvote'] and not is_downvote) or (not vote['is_downvote'] and is_downvote):
                # Opposite action, remove the vote
                Post.remove_post_vote(cursor, vote['id'])
            elif vote['is_downvote'] != is_downvote:
                # Different action, update the vote
                Post.update_post_vote(cursor, vote['id'], is_downvote)
            # If the action is the same as the existing vote, do nothing
        else:
            # No existing vote, insert new vote
            Post.insert_post_vote(cursor, post_id, user_id, is_downvote)

        conn.commit()

    except Exception as e:  # Catching a broader exception to handle any errors
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Vote updated successfully"}), 200