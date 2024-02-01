from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
from config import DevelopmentConfig, ProductionConfig, TestingConfig
from db_manager import DBManager

feed_bp = Blueprint('feed_bp', __name__)
db_manager = DBManager()

@feed_bp.route('/feed', methods=['GET'])
def get_feed():
    category_id = request.args.get('categoryId', type=int) # None if "All" screen
    user_id = request.args.get('userId', type=int)  # Assuming you can get the user_id from the request
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 10, type=int)

    conn = db_manager.get_db_connection()
    cursor = conn.cursor()

    # Use a different WHERE clause based on whether a specific category_id is provided
    if category_id:
        category_condition = "pc.category_id = %s"
        query_params = (category_id, count, (page - 1) * count)
    else:  # For "All" categories
        category_condition = "EXISTS (SELECT 1 FROM UserCategory AS uc WHERE uc.user_id = %s AND uc.category_id = pc.category_id)"
        query_params = (user_id, count, (page - 1) * count)

    query = f"""
    SELECT p.id, p.title, p.body, p.creation_time, p.update_time, p.user_id,
           GROUP_CONCAT(DISTINCT v.vendor_name ORDER BY v.vendor_name SEPARATOR ', ') AS vendors,
           GROUP_CONCAT(DISTINCT c.category_name ORDER BY c.category_name SEPARATOR ', ') AS categories
    FROM Post AS p
    LEFT JOIN PostVendor AS pv ON p.id = pv.post_id
    LEFT JOIN Vendor AS v ON pv.vendor_id = v.id
    INNER JOIN PostCategory AS pc ON p.id = pc.post_id
    INNER JOIN Category AS c ON pc.category_id = c.id
    WHERE {category_condition}
    GROUP BY p.id
    ORDER BY p.id DESC, p.creation_time DESC
    LIMIT %s OFFSET %s
    """
    cursor.execute(query, query_params)

    postBodies = cursor.fetchall()

    for post in postBodies:
        if post['categories']:
            post['categories'] = post['categories'].split(', ')
        else:
            post['categories'] = []

    cursor.close()
    conn.close()

    return jsonify(postBodies)
