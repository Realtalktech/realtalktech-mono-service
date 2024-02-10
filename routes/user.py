from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
import re
from apscheduler.schedulers.background import BackgroundScheduler
from trie import TrieNode, Trie
from werkzeug.security import generate_password_hash
from db_manager import DBManager
from responseFormatter import convert_keys_to_camel_case

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

@user_bp.route('/getUser', methods=['GET'])
def get_user_public_profile_by_username():
    """Get a user's public profile"""
    requested_username = request.args.get('publicUsername', type = str)
    requester_user_id = request.args.get('userId', type = str)
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()

    # Get user_id
    cursor.execute("""SELECT id FROM User WHERE username = %s""", (requested_username))
    requested_user_id = cursor.fetchone()['id']

    # Fetch user details
    cursor.execute("""
        SELECT full_name, username, current_company, linkedin_url, bio
        FROM User
        WHERE id = %s
    """, (requested_user_id,))
    user_details = cursor.fetchone()

    # Fetch associated vendor IDs
    cursor.execute("""
        SELECT vendor_id
        FROM UserVendor
        WHERE user_id = %s
    """, (requested_user_id,))
    vendor_ids = cursor.fetchall()
    
    # Convert vendor IDs to vendor names and check endorsements
    vendors_with_endorsements = []
    for vendor in vendor_ids:
        cursor.execute("""
            SELECT vendor_name
            FROM PublicVendor
            WHERE id = %s
        """, (vendor['vendor_id'],))
        vendor_name = cursor.fetchone()

        # Check for endorsement
        cursor.execute("""
            SELECT COUNT(*) AS endorsement_count
            FROM UserEndorsement
            WHERE endorser_user_id = %s AND vendor_id = %s
        """, (requester_user_id, vendor['vendor_id']))
        endorsement = cursor.fetchone()['endorsement_count'] > 0

        if vendor_name:
            vendors_with_endorsements.append({
                'vendor_name': vendor_name['vendor_name'],
                'endorsed_by_requester': endorsement
            })
    
    cursor.close()
    conn.close()

    user_details = convert_keys_to_camel_case(user_details)
    vendors_with_endorsements = [convert_keys_to_camel_case(item) for item in vendors_with_endorsements]

    return jsonify({'userDetails': user_details, 'vendors': vendors_with_endorsements})

    

@user_bp.route('/signup', methods=['PUT'])
def signup():
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    try:
        # Extract data from request
        data = request.json
        full_name = data.get('fullName')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        tech_stack = data.get('techstack', [])  # List of vendor names
        current_company = data.get('currentCompany')

        # Validate input
        if not (full_name and username and email and password and current_company):
            return jsonify({"error": "Missing required fields"}), 400
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"error": "Invalid email format"}), 400

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert user into database
        cursor.execute("""
            INSERT INTO User (full_name, username, current_company, email, password) 
            VALUES (%s, %s, %s, %s)
        """, (full_name, username, current_company, email, hashed_password))
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
        user_id = data.get('userId')
        new_first_name = data.get('firstName')
        new_last_name = data.get('lastName')
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
                SELECT v.vendor_name FROM PublicVendor AS v
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


@user_bp.route('/endorseUser', methods = ['PUT'])
def endorse_user():
    try:
        data = request.json
        endorser_user_id = data.get('endorserUserId')
        endorsee_username = data.get('endorseeUsername')
        vendor_id = data.get('vendorId')

        if not endorser_user_id and endorsee_username and vendor_id:
            return jsonify({"error": "Endorser User Id, Endorsee User Id, Vendor Id is required"}), 400

        cursor.execute("""SELECT id FROM User WHERE username = %s""", (endorsee_username))
        endorsee_user_id = cursor.fetchone()['id']

        conn = db_manager.get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO UserEndorsement (endorser_user_id, endorsee_user_id, vendor_id) VALUES (%s, %s, %s)""",
            (endorser_user_id, endorsee_user_id, vendor_id)
        )

        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Profile endorsed successfully"}), 200

