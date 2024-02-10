from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
from db_manager import DBManager

post_bp = Blueprint('post_bp', __name__)
db_manager = DBManager()

@post_bp.route('/makePost', methods=['POST'])
def make_post():
    try:
        data = request.json
        user_id = data.get('userId')
        title = data.get('title')
        body = data.get('body')
        categories = data.get('categories', [])  # List of category names
        is_anonymous = data.get('isAnonymous')
        vendors = data.get('vendors', []) # List of vendor names

        if not (user_id and title and body and is_anonymous):
            return jsonify({"error": "Missing required post information"}), 400

        conn = db_manager.get_db_connection()
        cursor = conn.cursor()

        # Insert post into database
        cursor.execute("""
            INSERT INTO Post (user_id, title, body, is_anonymous) 
            VALUES (%s, %s, %s, %s)
        """, (user_id, title, body, is_anonymous))
        post_id = cursor.lastrowid

        # Link post to categories
        for category_name in categories:
            cursor.execute("SELECT id FROM DiscussCategory WHERE category_name = %s", (category_name,))
            category = cursor.fetchone()
            if category:
                cursor.execute("""
                    INSERT INTO PostDiscussCategory (post_id, category_id) 
                    VALUES (%s, %s)
                """, (post_id, category['id']))
        
        # Link post to vendors
        for vendor_name in vendors:
            cursor.execute("SELECT id FROM DiscoverVendor WHERE vendor_name = %s", (vendor_name,))
            vendor = cursor.fetchone()
            if vendor:
                cursor.execute("""
                    INSERT INTO PostDiscoverVendor(post_id, vendor_id) 
                    VALUES (%s, %s)
                """, (post_id, vendor['id']))                

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Post created successfully", "post_id": post_id}), 201

@post_bp.route('/editPost', methods=['PUT'])
def edit_post():
    try:
        data = request.json
        post_id = data.get('postId')
        user_id = data.get('userId')  # Assuming you're tracking which user is making the request
        new_title = data.get('title')
        new_body = data.get('body')
        new_categories = set(data.get('categories', []))  # List of new category names

        if not post_id:
            return jsonify({"error": "Post ID is required"}), 400

        conn = db_manager.get_db_connection()
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
                SELECT c.category_name FROM DiscussCategory AS c
                JOIN PostDiscussCategory AS pc ON c.id = pc.category_id
                WHERE pc.post_id = %s
            """, (post_id,))
            current_categories = {row['category_name'] for row in cursor.fetchall()}

            # Categories to add
            for category_name in new_categories - current_categories:
                cursor.execute("SELECT id FROM DiscussCategory WHERE category_name = %s", (category_name,))
                category = cursor.fetchone()
                if category:
                    cursor.execute("""
                        INSERT INTO PostDiscussCategory (post_id, category_id) 
                        VALUES (%s, %s)
                    """, (post_id, category['id']))

            # Categories to remove
            for category_name in current_categories - new_categories:
                cursor.execute("SELECT id FROM DiscussCategory WHERE category_name = %s", (category_name,))
                category = cursor.fetchone()
                if category:
                    cursor.execute("""
                        DELETE FROM PostDiscussCategory 
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

@post_bp.route('/upvotePost', methods=['PUT'])
def upvote_post():
    try:
        data = request.json
        user_id = data.get('userId')
        post_id = data.get('postId')

        if not (user_id and post_id):
            return jsonify({"error": "User ID and Post ID are required"}), 400

        conn = db_manager.get_db_connection()
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

@post_bp.route('/removeUpvotePost', methods=['PUT'])
def remove_upvote_post():
    try:
        data = request.json
        user_id = data.get('userId')
        post_id = data.get('postId')

        if not (user_id and post_id):
            return jsonify({"error": "User ID and Post ID are required"}), 400

        conn = db_manager.get_db_connection()
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