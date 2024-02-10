from flask import Blueprint, jsonify, request, make_response
import pymysql
import pymysql.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash
from db_manager import DBManager

login_bp = Blueprint('login_bp', __name__)
db_manager = DBManager()

@login_bp.route('/signup', methods=['PUT'])
def signup():
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    try:
        # Extract data from request
        data = request.json
        full_name = data.get('fullname')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        tech_stack = data.get('techStack', [])  # List of vendor names
        current_company = data.get('currentCompany')
        categories_of_work = data.get('workCategories', []) # List of "what do you do?" names
        interest_areas = data.get('interestAreas', []) # List of interest area names

        # Initialize an empty list to collect the names of missing fields
        missing_fields = []

        # Check each field and add its name to the list if it is missing
        if not full_name:
            missing_fields.append('fullname')
        if not username:
            missing_fields.append('username')
        if not email:
            missing_fields.append('email')
        if not password:
            missing_fields.append('password')
        if not current_company:
            missing_fields.append('currentCompany')

        # If there are any missing fields, return an error message specifying them
        if missing_fields:
            missing_fields_str = ', '.join(missing_fields)  # Convert the list to a comma-separated string
            error_message = f"Missing required fields: {missing_fields_str}"
            return jsonify({"error": error_message}), 400
        

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"error": "Invalid email format"}), 400

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert user into database
        cursor.execute("""
            INSERT INTO User (full_name, username, current_company, email, password) 
            VALUES (%s, %s, %s, %s, %s)
        """, (full_name, username, current_company, email, hashed_password))
        user_id = cursor.lastrowid # Get ID of newly inserted user

        # Link categories of work to User in UserDiscussCategory for feed population
        for work_category in categories_of_work:
            cursor.execute("SELECT id FROM DiscussCategory WHERE category_name = %s", (work_category,))
            category = cursor.fetchone()
            if category:
                cursor.execute("""INSERT INTO UserDiscussCategory (user_id, category_id) VALUES (%s, %s)""",
                            (user_id, category['id']))
        
        # Link interest areas to user
        for area in interest_areas:
            cursor.execute("SELECT id FROM InterestArea WHERE interest_area_name = %s", (area,))
            interest_area_id = cursor.fetchone()
            if interest_area_id:
                cursor.execute("""INSERT INTO UserInterestArea (user_id, interest_area_id) VALUES (%s, %s)""",
                            (user_id, interest_area_id['id']))                

        # Link tech stack to user
        for tech in tech_stack:
            cursor.execute("SELECT id FROM PublicVendor WHERE vendor_name = %s", (tech,))
            vendor = cursor.fetchone()
            if vendor:
                cursor.execute("""
                    INSERT INTO UserPublicVendor (user_id, vendor_id) 
                    VALUES (%s, %s)
                """, (user_id, vendor['id']))

        conn.commit()

        # Prepare response and set cookie
        response = make_response(jsonify({"message": "Signup successful"}), 201)
        response.set_cookie('userId', str(user_id), httponly=True)  # Setting the user ID as a cookie
        return response

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@login_bp.route('/login', methods=['POST'])
def login():
    # Extract username and password from the request
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Connect to the database
    conn = db_manager.get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # Fetch the user by username
        cursor.execute("SELECT id, password FROM User WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            # Authentication successful
            response = make_response(jsonify({"message": "Login successful"}), 200)
            # Issue a secure, HttpOnly cookie with the user ID
            response.set_cookie('userId', str(user['id']), httponly=True, secure=True)  # secure=True ensures the cookie is sent over HTTPS
            return response
        else:
            # Authentication failed
            return jsonify({"error": "Invalid username or password"}), 401
    finally:
        cursor.close()
        conn.close()    