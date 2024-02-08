from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
import re
from apscheduler.schedulers.background import BackgroundScheduler
from trie import TrieNode, Trie
from werkzeug.security import generate_password_hash
from db_manager import DBManager

user_bp = Blueprint('user_bp', __name__)
db_manager = DBManager()

# trie = Trie()

# def update_trie():
#     conn = db_manager.get_db_connection()
#     try:
#         cursor = conn.cursor()
#         cursor.execute("SELECT vendor_name FROM PublicVendor")
#         for row in cursor.fetchall():
#             trie.insert(row['vendor_name'].lower())
#     finally:
#         conn.close()

# scheduler = BackgroundScheduler()
# scheduler.add_job(func=update_trie, trigger="interval", hours=1) # Update every hour
# scheduler.start()

# @user_bp.route('/autocomplete', methods=['GET'])
# def autocomplete():
#     prefix = request.args.get('prefix', '')
#     suggestions = trie.autocomplete(prefix)
#     return jsonify(suggestions)

@user_bp.route('/signup', methods=['PUT'])
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
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO User (first_name, last_name, username, email, password) 
            VALUES (%s, %s, %s, %s, %s)
        """, (first_name, last_name, username, email, hashed_password))
        user_id = cursor.lastrowid

        # Link tech stack to user
        for tech in tech_stack:
            cursor.execute("SELECT id FROM PublicVendor WHERE vendor_name = %s", (tech,))
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

@user_bp.route('/editProfile', methods=['PUT'])
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

        conn = db_manager.get_db_connection()
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
                cursor.execute("SELECT id FROM PublicVendor WHERE vendor_name = %s", (tech,))
                vendor = cursor.fetchone()
                if vendor:
                    cursor.execute("""
                        INSERT INTO UserVendor (user_id, vendor_id) 
                        VALUES (%s, %s)
                    """, (user_id, vendor['id']))

            # Tech stack to remove
            for tech in current_tech_stack - new_tech_stack:
                cursor.execute("SELECT id FROM PublicVendor WHERE vendor_name = %s", (tech,))
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
