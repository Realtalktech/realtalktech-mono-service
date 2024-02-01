from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
from config import DevelopmentConfig, ProductionConfig, TestingConfig
from db_manager import DBManager

comment_bp = Blueprint('comment_bp', __name__)
db_manager = DBManager()

@comment_bp.route('/getComments', methods=['GET'])
def get_comments():
    post_id = request.args.get('postId', type=int)
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 10, type=int)

    conn = db_manager.get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT c.id, c.user_id, c.comment_text, c.id, c.creation_time
    FROM Comment AS c
    WHERE c.post_id = %s
    ORDER BY c.id DESC
    LIMIT %s OFFSET %s
    """
    cursor.execute(query, (post_id, count, (page - 1) * count))
    comments = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(comments)

@comment_bp.route('/makeComment', methods=['POST'])
def make_comment():
    try:
        data = request.json
        post_id = data.get('post_id')
        user_id = data.get('user_id')
        comment_text = data.get('comment_text')

        # Validate input
        if not (post_id and user_id and comment_text):
            return jsonify({"error": "Missing required comment information"}), 400

        conn = db_manager.get_db_connection()
        cursor = conn.cursor()

        # Insert comment into the database
        cursor.execute("""
            INSERT INTO Comment (post_id, user_id, comment_text)
            VALUES (%s, %s, %s)
        """, (post_id, user_id, comment_text))
        comment_id = cursor.lastrowid

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Comment added successfully", "comment_id": comment_id}), 201

@comment_bp.route('/upvoteComment', methods=['PUT'])
def upvote_comment():
    try:
        data = request.json
        user_id = data.get('user_id')
        comment_id = data.get('comment_id')

        if not (user_id and comment_id):
            return jsonify({"error": "User ID and Comment ID are required"}), 400

        conn = db_manager.get_db_connection()
        cursor = conn.cursor()

        # Check if the user has already upvoted this comment
        cursor.execute("""
            SELECT id FROM CommentUpvote 
            WHERE user_id = %s AND comment_id = %s
        """, (user_id, comment_id))
        if cursor.fetchone():
            return jsonify({"error": "Comment already upvoted by this user"}), 409

        # Insert upvote into the CommentUpvote table
        cursor.execute("""
            INSERT INTO CommentUpvote (comment_id, user_id)
            VALUES (%s, %s)
        """, (comment_id, user_id))

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Comment upvoted successfully"}), 200

@comment_bp.route('/removeUpvoteComment', methods=['PUT'])
def remove_upvote_comment():
    try:
        data = request.json
        user_id = data.get('user_id')
        comment_id = data.get('comment_id')

        if not (user_id and comment_id):
            return jsonify({"error": "User ID and Comment ID are required"}), 400

        conn = db_manager.get_db_connection()
        cursor = conn.cursor()

        # Delete upvote from the CommentUpvote table
        cursor.execute("""
            DELETE FROM CommentUpvote
            WHERE user_id = %s AND comment_id = %s
        """, (user_id, comment_id))

        # Check if the delete operation was successful
        if cursor.rowcount == 0:
            return jsonify({"error": "No upvote found or user did not upvote this comment"}), 404

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Comment upvote removed successfully"}), 200