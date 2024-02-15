from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
from utils import DBManager, convert_keys_to_camel_case, token_required
from models import User

feed_bp = Blueprint('feed_bp', __name__)
db_manager = DBManager()

@feed_bp.route('/feed', methods=['GET'])
@token_required
def get_feed(user_id):
    category_id = request.args.get('categoryId', type=int)  # None if "All" screen
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 10, type=int)

    conn = db_manager.get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if category_id:
        category_condition = "pc.category_id = %s"
        query_params = (category_id, user_id, count, (page - 1) * count)
    else:
        category_condition = "EXISTS (SELECT 1 FROM UserDiscussCategory AS uc WHERE uc.user_id = %s AND uc.category_id = pc.category_id)"
        query_params = (user_id, user_id, count, (page - 1) * count)

    query = f"""
    SELECT p.id, p.title, p.body, p.creation_time, p.update_time, p.user_id, p.is_anonymous,
           GROUP_CONCAT(DISTINCT v.vendor_name ORDER BY v.vendor_name SEPARATOR ', ') AS vendors,
           GROUP_CONCAT(DISTINCT c.category_name ORDER BY c.category_name SEPARATOR ', ') AS categories
    FROM Post AS p
    LEFT JOIN PostDiscoverVendor AS pv ON p.id = pv.post_id
    LEFT JOIN DiscoverVendor AS v ON pv.vendor_id = v.id
    INNER JOIN PostDiscussCategory AS pc ON p.id = pc.post_id
    INNER JOIN DiscussCategory AS c ON pc.category_id = c.id
    WHERE {category_condition}
    GROUP BY p.id
    ORDER BY p.id DESC, p.creation_time DESC
    LIMIT %s OFFSET %s
    """
    cursor.execute(query, query_params)
    post_bodies = cursor.fetchall()

    for post in post_bodies:
        # Process categories and vendors
        post['categories'] = post['categories'].split(', ') if post['categories'] else []
        post['vendors'] = post['vendors'].split(', ') if post['vendors'] else []

        # Set anonymous user information
        if post['is_anonymous']:
            username = ""
            post_author_id = -1
        else:
            cursor.execute("""SELECT username FROM User WHERE id = %s""", (post['user_id'],))
            user_info = cursor.fetchone()
            username = user_info['username'] if user_info else ""
            post_author_id = post.pop('user_id')

        # Process user information
        post['user'] = {"id": post_author_id, "username": username}

        # Determine the user's voting status
        cursor.execute("""
            SELECT is_downvote FROM PostUpvote
            WHERE post_id = %s AND user_id = %s
        """, (post['id'], user_id))
        vote_result = cursor.fetchone()
        post['user_vote'] = vote_result['is_downvote'] if vote_result is not None else None

        # Calculate number of upvotes and downvotes
        cursor.execute("""
            SELECT SUM(is_downvote = 0) AS upvotes, SUM(is_downvote = 1) AS downvotes
            FROM PostUpvote WHERE post_id = %s
        """, (post["id"],))
        vote_counts = cursor.fetchone()
        post['num_upvotes'] = vote_counts['upvotes'] if vote_counts else 0
        post['num_downvotes'] = vote_counts['downvotes'] if vote_counts else 0

        # Calculate number of comments
        cursor.execute("""SELECT COUNT(*) AS num_comments FROM Comment WHERE post_id = %s""", (post["id"],))
        num_comments = cursor.fetchone()
        post['num_comments'] = num_comments['num_comments'] if num_comments else 0

        # Convert timestamps to ISO format
        post['created_timestamp'] = post.pop('creation_time').isoformat()
        post['updated_timestamp'] = post.pop('update_time').isoformat()

    cursor.close()
    conn.close()

    # Convert keys to camel case and prepare response
    post_bodies = [convert_keys_to_camel_case(post) for post in post_bodies]  # Assuming this function is defined

    # Prepare metadata
    metadata = {
        'categoryId': category_id,
        'searcherUserId': user_id,
        'page': page,
        'count': count
    }

    return jsonify({"metadata": metadata, "posts": post_bodies})