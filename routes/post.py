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
        print(data)
        title = data.get('title')
        body = data.get('body')
        categories = data.get('categories', [])  # List of category names
        is_anonymous = data.get('isAnonymous')
        vendors = data.get('vendors', []) # List of vendor names

        if not (title and body and is_anonymous):
            missing_fields = ''
            if not title: missing_fields += 'title '
            if not body: missing_fields += 'body '
            if not is_anonymous: missing_fields += 'anonymity status '
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
def upvote_post(user_id):
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401  # 401 Unauthorized
    try:
        data = request.json
        post_id = data.get('postId')

        if not (user_id and post_id):
            return jsonify({"error": "User ID and Post ID are required"}), 400

        conn = db_manager.get_db_connection()
        cursor = conn.cursor()

        # Check if the user has already upvoted this post
        if Post.is_post_liked_by_user(user_id, post_id):
            return jsonify({"error": "Post was already liked by user"}), 409

        # Insert upvote into the PostUpvote table
        Post.upvote_post_with_id(user_id, post_id)

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Post upvoted successfully"}), 200

@post_bp.route('/removeUpvotePost', methods=['PUT'])
def remove_upvote_post():
    user_id = request.cookies.get('userId')
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401  # 401 Unauthorized
    try:
        data = request.json
        post_id = data.get('postId')

        if not (user_id and post_id):
            return jsonify({"error": "User ID and Post ID are required"}), 400

        conn = db_manager.get_db_connection()
        cursor = conn.cursor()

        if not Post.is_post_liked_by_user(user_id, post_id):
            return jsonify({"error": "User has not liked post"}), 409
        
        Post.remove_upvote_post_with_id(cursor, user_id, post_id)

        # Check if the delete operation was successful
        if cursor.rowcount == 0:
            return jsonify({"error": "No upvote found or user did not upvote this post"}), 404

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Post upvote removed successfully"}), 200