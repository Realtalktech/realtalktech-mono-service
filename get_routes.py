from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
from config import DevelopmentConfig

# Database connection details
HOST="realtalktechrdsstack-realtalktechdbinstance-c7ciisdczocf.cnqm62ueodz0.us-east-1.rds.amazonaws.com"
USER="admin"
PASSWORD="ReallyRealAboutTech123!"
DB = "RealTalkTechDB"

get_bp = Blueprint('get_bp', __name__)

def get_db_connection():
    return pymysql.connect(host=HOST,
                           user=USER,
                           password=PASSWORD,
                           db=DB,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

@get_bp.route('/feed', methods=['GET'])
def get_feed():
    # Test change
    category_id = request.args.get('categoryId', type=int) # None if "All" screen
    user_id = request.args.get('userId', type=int)  # Assuming you can get the user_id from the request
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 10, type=int)

    conn = get_db_connection()
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

@get_bp.route('/getComments', methods=['GET'])
def get_comments():
    post_id = request.args.get('postId', type=int)
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 10, type=int)

    conn = get_db_connection()
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

@get_bp.route('/discover', methods=['GET'])
def get_vendors():
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 10, type=int)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT id, vendor_name, description, vendor_url, creation_time, update_time
    FROM Vendor
    ORDER BY id
    LIMIT %s OFFSET %s
    """
    cursor.execute(query, (count, (page - 1) * count))

    vendors = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(vendors)

@get_bp.route('/getVendor', methods=['GET'])
def get_vendor():
    vendor_id = request.args.get('vendor_id', type=int)

    if not vendor_id:
        return jsonify({"error": "Vendor ID is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT id, vendor_name, description, vendor_url, creation_time, update_time
    FROM Vendor
    WHERE id = %s
    """
    cursor.execute(query, (vendor_id,))

    vendor = cursor.fetchone()

    cursor.close()
    conn.close()

    if vendor:
        return jsonify(vendor)
    else:
        return jsonify({"error": "Vendor not found"}), 404