from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
import re
from config import DevelopmentConfig
from werkzeug.security import generate_password_hash

# Database connection details
HOST="realtalktechrdsstack-realtalktechdbinstance-c7ciisdczocf.cnqm62ueodz0.us-east-1.rds.amazonaws.com"
USER="admin"
PASSWORD="ReallyRealAboutTech123!"
DB = "RealTalkTechDB"

post_put_bp = Blueprint('post_put_bp', __name__)

def get_db_connection():
    return pymysql.connect(host=HOST,
                           user=USER,
                           password=PASSWORD,
                           db=DB,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

@post_put_bp.route('/signup', methods=['PUT'])
def signup():
    try:
        # Extract data from request
        data = request.json
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        tech_stack = data.get('techstack', [])  # List of vendor names

        # Validate input
        if not (first_name and username and email and password):
            return jsonify({"error": "Missing required fields"}), 400
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"error": "Invalid email format"}), 400

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert user into database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO User (first_name, last_name, username, email, password) 
            VALUES (%s, %s, %s, %s, %s)
        """, (first_name, last_name, username, email, hashed_password))
        user_id = cursor.lastrowid

        # Link tech stack to user
        for tech in tech_stack:
            cursor.execute("SELECT id FROM Vendor WHERE vendor_name = %s", (tech,))
            vendor = cursor.fetchone()
            if vendor:
                cursor.execute("""
                    INSERT INTO UserVendor (user_id, vendor_id) 
                    VALUES (%s, %s)
                """, (user_id, vendor['id']))

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Signup successful", "user_id": user_id}), 201

@post_put_bp.route('/editProfile', methods=['PUT'])
def edit_profile():
    try:
        data = request.json
        user_id = data.get('user_id')
        new_first_name = data.get('first_name')
        new_last_name = data.get('last_name')
        new_email = data.get('email')
        new_password = data.get('password')  # Assuming password change is allowed
        new_tech_stack = set(data.get('techstack', []))  # List of new vendor names

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Update user information
        cursor.execute("""
            UPDATE User SET first_name = COALESCE(%s, first_name), 
                            last_name = COALESCE(%s, last_name),
                            email = COALESCE(%s, email),
                            password = COALESCE(%s, password),
                            update_time = CURRENT_TIMESTAMP(3)
            WHERE id = %s
        """, (new_first_name, new_last_name, new_email, new_password, user_id))

        # Update tech stack
        if new_tech_stack:
            # Fetch current tech stack of the user
            cursor.execute("""
                SELECT v.vendor_name FROM Vendor AS v
                JOIN UserVendor AS uv ON v.id = uv.vendor_id
                WHERE uv.user_id = %s
            """, (user_id,))
            current_tech_stack = {row['vendor_name'] for row in cursor.fetchall()}

            # Tech stack to add
            for tech in new_tech_stack - current_tech_stack:
                cursor.execute("SELECT id FROM Vendor WHERE vendor_name = %s", (tech,))
                vendor = cursor.fetchone()
                if vendor:
                    cursor.execute("""
                        INSERT INTO UserVendor (user_id, vendor_id) 
                        VALUES (%s, %s)
                    """, (user_id, vendor['id']))

            # Tech stack to remove
            for tech in current_tech_stack - new_tech_stack:
                cursor.execute("SELECT id FROM Vendor WHERE vendor_name = %s", (tech,))
                vendor = cursor.fetchone()
                if vendor:
                    cursor.execute("""
                        DELETE FROM UserVendor 
                        WHERE user_id = %s AND vendor_id = %s
                    """, (user_id, vendor['id']))

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Profile updated successfully"}), 200


@post_put_bp.route('/makePost', methods=['POST'])
def make_post():
    try:
        data = request.json
        user_id = data.get('user_id')
        title = data.get('title')
        body = data.get('body')
        categories = data.get('categories', [])  # List of category names

        if not (user_id and title and body):
            return jsonify({"error": "Missing required post information"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert post into database
        cursor.execute("""
            INSERT INTO Post (user_id, title, body) 
            VALUES (%s, %s, %s)
        """, (user_id, title, body))
        post_id = cursor.lastrowid

        # Link post to categories
        for category_name in categories:
            cursor.execute("SELECT id FROM Category WHERE category_name = %s", (category_name,))
            category = cursor.fetchone()
            if category:
                cursor.execute("""
                    INSERT INTO PostCategory (post_id, category_id) 
                    VALUES (%s, %s)
                """, (post_id, category['id']))

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Post created successfully", "post_id": post_id}), 201

@post_put_bp.route('/editPost', methods=['PUT'])
def edit_post():
    try:
        data = request.json
        post_id = data.get('post_id')
        user_id = data.get('user_id')  # Assuming you're tracking which user is making the request
        new_title = data.get('title')
        new_body = data.get('body')
        new_categories = set(data.get('categories', []))  # List of new category names

        if not post_id:
            return jsonify({"error": "Post ID is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Update post title and body if provided
        if new_title or new_body:
            cursor.execute("""
                UPDATE Post SET title = COALESCE(%s, title), 
                                body = COALESCE(%s, body),
                                update_time = CURRENT_TIMESTAMP(3)
                WHERE id = %s AND user_id = %s
            """, (new_title, new_body, post_id, user_id))

        # Update post categories
        if new_categories:
            # Fetch current categories of the post
            cursor.execute("""
                SELECT c.category_name FROM Category AS c
                JOIN PostCategory AS pc ON c.id = pc.category_id
                WHERE pc.post_id = %s
            """, (post_id,))
            current_categories = {row['category_name'] for row in cursor.fetchall()}

            # Categories to add
            for category_name in new_categories - current_categories:
                cursor.execute("SELECT id FROM Category WHERE category_name = %s", (category_name,))
                category = cursor.fetchone()
                if category:
                    cursor.execute("""
                        INSERT INTO PostCategory (post_id, category_id) 
                        VALUES (%s, %s)
                    """, (post_id, category['id']))

            # Categories to remove
            for category_name in current_categories - new_categories:
                cursor.execute("SELECT id FROM Category WHERE category_name = %s", (category_name,))
                category = cursor.fetchone()
                if category:
                    cursor.execute("""
                        DELETE FROM PostCategory 
                        WHERE post_id = %s AND category_id = %s
                    """, (post_id, category['id']))

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Post updated successfully"}), 200

@post_put_bp.route('/upvotePost', methods=['PUT'])
def upvote_post():
    try:
        data = request.json
        user_id = data.get('user_id')
        post_id = data.get('post_id')

        if not (user_id and post_id):
            return jsonify({"error": "User ID and Post ID are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the user has already upvoted this post
        cursor.execute("""
            SELECT id FROM PostUpvote 
            WHERE user_id = %s AND post_id = %s
        """, (user_id, post_id))
        if cursor.fetchone():
            return jsonify({"error": "Post already upvoted by this user"}), 409

        # Insert upvote into the PostUpvote table
        cursor.execute("""
            INSERT INTO PostUpvote (post_id, user_id)
            VALUES (%s, %s)
        """, (post_id, user_id))

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Post upvoted successfully"}), 200

@post_put_bp.route('/removeUpvotePost', methods=['PUT'])
def remove_upvote_post():
    try:
        data = request.json
        user_id = data.get('user_id')
        post_id = data.get('post_id')

        if not (user_id and post_id):
            return jsonify({"error": "User ID and Post ID are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Delete upvote from the PostUpvote table
        cursor.execute("""
            DELETE FROM PostUpvote
            WHERE user_id = %s AND post_id = %s
        """, (user_id, post_id))

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


@post_put_bp.route('/makeComment', methods=['POST'])
def make_comment():
    try:
        data = request.json
        post_id = data.get('post_id')
        user_id = data.get('user_id')
        comment_text = data.get('comment_text')

        # Validate input
        if not (post_id and user_id and comment_text):
            return jsonify({"error": "Missing required comment information"}), 400

        conn = get_db_connection()
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

@post_put_bp.route('/upvoteComment', methods=['PUT'])
def upvote_comment():
    try:
        data = request.json
        user_id = data.get('user_id')
        comment_id = data.get('comment_id')

        if not (user_id and comment_id):
            return jsonify({"error": "User ID and Comment ID are required"}), 400

        conn = get_db_connection()
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

@post_put_bp.route('/removeUpvoteComment', methods=['PUT'])
def remove_upvote_comment():
    try:
        data = request.json
        user_id = data.get('user_id')
        comment_id = data.get('comment_id')

        if not (user_id and comment_id):
            return jsonify({"error": "User ID and Comment ID are required"}), 400

        conn = get_db_connection()
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

@post_put_bp.route('/addVendor', methods=['POST'])
def add_vendor():
    try:
        data = request.json
        vendor_name = data.get('vendor_name')
        description = data.get('description')
        vendor_url = data.get('vendor_url')

        if not vendor_name:
            return jsonify({"error": "Vendor name is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert new vendor into the Vendor table
        cursor.execute("""
            INSERT INTO Vendor (vendor_name, description, vendor_url)
            VALUES (%s, %s, %s)
        """, (vendor_name, description, vendor_url))
        vendor_id = cursor.lastrowid

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Vendor added successfully", "vendor_id": vendor_id}), 201

@post_put_bp.route('/updateVendor', methods=['PUT'])
def update_vendor():
    try:
        data = request.json
        vendor_id = data.get('vendor_id')
        new_vendor_name = data.get('vendor_name')
        new_description = data.get('description')
        new_vendor_url = data.get('vendor_url')

        if not vendor_id:
            return jsonify({"error": "Vendor ID is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Update vendor details in the Vendor table
        cursor.execute("""
            UPDATE Vendor 
            SET vendor_name = COALESCE(%s, vendor_name), 
                description = COALESCE(%s, description),
                vendor_url = COALESCE(%s, vendor_url)
            WHERE id = %s
        """, (new_vendor_name, new_description, new_vendor_url, vendor_id))

        # Check if the update operation was successful
        if cursor.rowcount == 0:
            return jsonify({"error": "Vendor not found or no new data provided"}), 404

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Vendor updated successfully"}), 200




