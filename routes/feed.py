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
    category_id = request.args.get('categoryId', type=int) # None if "All" screen
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 10, type=int)

    conn = db_manager.get_db_connection()
    cursor = conn.cursor()

    query = f"""
    SELECT p.id, p.title, p.body, p.creation_time, p.update_time, p.user_id, p.is_anonymous,
        GROUP_CONCAT(DISTINCT v.vendor_name ORDER BY v.vendor_name SEPARATOR ', ') AS vendors,
        (SELECT GROUP_CONCAT(DISTINCT c.category_name ORDER BY c.category_name SEPARATOR ', ')
            FROM PostDiscussCategory AS pc
            INNER JOIN DiscussCategory AS c ON pc.category_id = c.id
            WHERE pc.post_id = p.id) AS categories
    FROM Post AS p
    LEFT JOIN PostDiscoverVendor AS pv ON p.id = pv.post_id
    LEFT JOIN DiscoverVendor AS v ON pv.vendor_id = v.id
    WHERE {('EXISTS (SELECT 1 FROM PostDiscussCategory AS pc WHERE pc.post_id = p.id AND pc.category_id = %s)' if category_id else 'EXISTS (SELECT 1 FROM UserDiscussCategory AS uc WHERE uc.user_id = %s AND EXISTS (SELECT 1 FROM PostDiscussCategory AS pc WHERE pc.post_id = p.id AND pc.category_id = uc.category_id))')}
    GROUP BY p.id
    ORDER BY p.id DESC, p.creation_time DESC
    LIMIT %s OFFSET %s
    """
    query_params = (category_id if category_id else user_id, count, (page - 1) * count)
    cursor.execute(query, query_params)
    
    post_bodies = cursor.fetchall()

    for post in post_bodies:
        # Process categories
        if post['categories']:
            post['categories'] = post['categories'].split(', ')
        else:
            post['categories'] = []
        
        # Process vendors
        if post['vendors']:
            post['vendors'] = post['vendors'].split(', ')
        else:
            post['vendors'] = []

        is_anonymous = post.pop('is_anonymous')

        if is_anonymous:
            username = ""
            post.pop('user_id')
            post_author_id = -1

        else:
            cursor.execute("""SELECT username FROM User WHERE id = %s""", (post['user_id']))
            username = cursor.fetchone()['username']
            post_author_id = post.pop('user_id')
    
        
        # Process user information
        post['user'] = {"id": post_author_id, "username": username}

        # Calculate number of upvotes on each post
        cursor.execute("""SELECT COUNT(*) FROM PostUpvote WHERE post_id = %s AND is_downvote = %s""", (post["id"], False))
        num_likes = cursor.fetchall()
        post['num_upvotes'] = num_likes[0]['COUNT(*)']

        # Calculate number of downvotes on each post
        cursor.execute("""SELECT COUNT(*) FROM PostUpvote WHERE post_id = %s AND is_downvote = %s""", (post["id"], True))
        num_likes = cursor.fetchall()
        post['num_downvotes'] = num_likes[0]['COUNT(*)']

        # Check if the user has already voted on post
        cursor.execute("""
            SELECT id, is_downvote FROM PostUpvote 
            WHERE user_id = %s AND post_id = %s
        """, (user_id, post['id']))
        vote = cursor.fetchone()
        if not vote:
            post['user_vote'] = None
        elif vote['is_downvote']:
            post['user_vote'] = False
        else:
            post['user_vote'] = True

        # Calculate number of comments on each post
        cursor.execute("""SELECT COUNT(*) FROM Comment WHERE post_id = %s""", (post["id"]))
        num_comments = cursor.fetchall()
        post['num_comments'] = num_comments[0]['COUNT(*)']

        # Get comment ids for each post
        cursor.execute("""SELECT id FROM Comment WHERE post_id = %s""", (post["id"]))
        comments = cursor.fetchall()
        comment_ids = [comment['id'] for comment in comments]

        post['comment_ids'] = comment_ids


        # Convert timestamps to ISO
        post['created_timestamp'] = post.pop('creation_time').isoformat()
        post['updated_timestamp'] = post.pop('update_time').isoformat()

    cursor.close()
    conn.close()

    post_bodies = [convert_keys_to_camel_case(post) for post in post_bodies]

    # Prepare metadata
    metadata = {
        'categoryId': category_id,
        'searcherUserId': user_id,
        'page': page,
        'count': count
    }

    return jsonify({"metadata": metadata, "posts": post_bodies})
