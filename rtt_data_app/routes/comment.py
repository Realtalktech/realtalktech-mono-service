from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
from rtt_data_app.utils import DBManager,token_required
from rtt_data_app.utils.deprecated.responseFormatter import convert_keys_to_camel_case

comment_bp = Blueprint('comment_bp', __name__)
db_manager = DBManager()

@comment_bp.route('/getCommentsForPost', methods=['GET'])
@token_required
def get_comments(user_id):
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401  # 401 Unauthorized
    post_id = request.args.get('postId', type=int)
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 10, type=int)

    conn = db_manager.get_db_connection()
    cursor = conn.cursor()

    # Query to fetch comments and their upvote count
    query = """
        SELECT 
            c.id, 
            c.user_id, 
            u.username, 
            c.comment_text, 
            c.creation_time, 
            c.update_time,
            (SELECT COUNT(*) FROM CommentUpvote WHERE comment_id = c.id AND is_downvote = FALSE) as total_upvotes,
            (SELECT COUNT(*) FROM CommentUpvote WHERE comment_id = c.id AND is_downvote = TRUE) as total_downvotes,
            (
                SELECT CASE 
                    WHEN COUNT(*) > 0 AND is_downvote = FALSE THEN TRUE
                    WHEN COUNT(*) > 0 AND is_downvote = TRUE THEN FALSE
                    ELSE NULL 
                END
                FROM CommentUpvote 
                WHERE comment_id = c.id AND user_id = %s
            ) as user_vote
        FROM Comment AS c
        JOIN User AS u ON c.user_id = u.id
        WHERE c.post_id = %s
        ORDER BY c.id DESC
        LIMIT %s OFFSET %s
    """
    cursor.execute(query, (user_id, post_id, count, (page - 1) * count))
    comment_bodies = cursor.fetchall()

    for comment in comment_bodies:
        # Get username for response body
        cursor.execute("""SELECT username FROM User WHERE id = %s""", (comment['user_id']))
        username = cursor.fetchone()['username']
        comment_user_id = comment.pop('user_id')

        # Process user information
        comment['user'] = {"id": comment_user_id, "username": username}

        # Get tags associated with comment
        cursor.execute(
            """SELECT tagged_user_id FROM CommentTag WHERE comment_id = %s""",
            (comment['id'])
        )
        tagged_ids = cursor.fetchall()
        comment['tagged_usernames'] = []
        for item in tagged_ids:
            tagged_user_id = item['tagged_user_id']
            cursor.execute("""SELECT username FROM User WHERE id = %s""", (tagged_user_id))
            tagged_username = cursor.fetchone()['username']
            comment['tagged_usernames'].append(tagged_username)

    cursor.close()
    conn.close()

    # Prepare metadata
    metadata = {
        'postId': post_id,
        'searcherUserId': user_id,
        'page': page,
        'count': count
    }

    # Format response
    comment_bodies = [convert_keys_to_camel_case(comment) for comment in comment_bodies]

    return jsonify({"metadata": metadata, "comments": comment_bodies})


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