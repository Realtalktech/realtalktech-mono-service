from flask import Blueprint, jsonify, request, make_response
import pymysql
import pymysql.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash
from auth import Authorizer
from models import User
from utils import DBManager

login_bp = Blueprint('login_bp', __name__)
db_manager = DBManager()

def extract_signup_fields(data):
        full_name = data.get('fullname')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        tech_stack = data.get('techStack', [])  # List of vendor names from "setup your profile"
        current_company = data.get('currentCompany')
        industry_involvement = data.get('industryInvolvement', []) # List of "what industry are you in?" names
        categories_of_work = data.get('workCategories', []) # List of "what do you do?" names
        linkedin_url = data.get('linkedinUrl')
        bio = data.get('bio')
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
        
        return (missing_fields, full_name, username, email, 
                password, tech_stack, current_company, industry_involvement, 
                categories_of_work, interest_areas, linkedin_url, bio)

@login_bp.route('/signup', methods=['PUT'])
def signup():
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    try:
        # Extract data from request
        data = request.json
        (missing_fields, full_name, username, 
         email, password, tech_stack, current_company, industry_involvement, 
         categories_of_work, interest_areas, linkedin_url, bio) = extract_signup_fields(data)
        
        # If there are any missing fields, return an error message specifying them
        if len(missing_fields) > 0:
            missing_fields_str = ', '.join(missing_fields)  # Convert the list to a comma-separated string
            error_message = f"Missing required fields: {missing_fields_str}"
            return jsonify({"error": error_message}), 400
        
        # Check standard email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"error": "Invalid email format"}), 400

        new_user = User(
            id = None,
            full_name=full_name,
            username=username,
            email=email,
            password=password,
            linkedin_url=linkedin_url,
            tech_stack_vendor_names=tech_stack,
            current_company=current_company,
            industry_involvement_names=industry_involvement,
            subscribed_discuss_category_names=categories_of_work,
            interest_area_names=interest_areas,
            bio = bio
        )

        # Create new user and get id
        new_user.create_user(cursor)
        conn.commit()

        # Issue token upon successful sign up
        token = Authorizer.generate_token(new_user.id)

        # Prepare response and generate token
        response = make_response(
            jsonify(
                {
                    "message": "Signup successful",
                    "token": token
                }
            ), 201
        )
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
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Connect to the database
    conn = db_manager.get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # Create user object
        user = User.authenticate_and_create_returning_user(cursor, username, password)
        if not user:
            return jsonify({"error": "Invalid username or password"}), 401
        else:
            # Authentication successful

            # Construct user response
            subsribed_discuss_categories = []
            for idx, name in enumerate(user.subscribed_discuss_category_names):
                subsribed_discuss_categories.append({
                    'id': user.subscribed_discuss_category_ids[idx],
                    'name': name
                })
            
            industry_involvement = []
            for idx, name in enumerate(user.industry_involvement_names):
                industry_involvement.append({
                    'id': user.industry_involvement_ids[idx],
                    'name': name
                })
            
            tech_stack = []
            for idx, name in enumerate(user.tech_stack_vendor_names):
                tech_stack.append({
                    'id': user.tech_stack_vendor_ids[idx],
                    'name': name
                })
            
            interest_areas = []
            for idx, name in enumerate(user.interest_area_names):
                interest_areas.append({
                    'id': user.interest_area_ids[idx],
                    'name': name
                })

            user_response = {
                'id': user.id,
                'fullName': user.full_name,
                'username': user.username,
                'currentCompany': user.current_company,
                'email': user.email,
                'linkedin_url': user.linkedin_url,
                'bio': user.bio,
                'occupationalAreas': subsribed_discuss_categories,
                'industryInvolvement': industry_involvement,
                'techstack': tech_stack,
                'interestAreas': interest_areas
            }

            # Issue a secure token
            token = Authorizer.generate_token(user.id)
            response = make_response(
                jsonify(
                    {
                        "message": "Login successful",
                        'userDetails': user_response,
                        "token": token
                    }
                ), 200
            )
            return response
        
    finally:
        cursor.close()
        conn.close()

# on signup, theres a few dropdowns where the user has to select
# industry,
# categories,
# interests
# we need lists for all those, thhough categories is the same list as in discuss


@login_bp.route('/onboard')
def get_interest_areas():
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT id, interest_area_name FROM InterestArea""")
    interest_areas = cursor.fetchall()
    cursor.execute("""SELECT id, industry_name FROM Industry""")
    industries = cursor.fetchall()
    cursor.execute("""SELECT id, category_name FROM DiscussCategory""")
    subscription_areas = cursor.fetchall()
    cursor.execute("""SELECT id, vendor_name FROM PublicVendor""")
    tech_stack = cursor.fetchall()

    return jsonify({
        'interestAreas': interest_areas,
        'industries': industries,
        'subscriptionAreas': subscription_areas,
        'techstack': tech_stack
    })

# @login_bp.route('/industryDropdown')
# def get_industry_areas():
#     conn = db_manager.get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("""SELECT id, industry_name FROM Industry""")
#     industries = cursor.fetchall()
#     return jsonify({
#         'industries': industries
#     })

# @login_bp('/categoryDropdown')
# def get_subscription_areas():
#     conn = db_manager.get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("""SELECT id, category_name FROM DiscussCategory""")
#     subscription_areas = cursor.fetchall()
#     return jsonify({
#         'subscriptionAreas': subscription_areas
#     })


@login_bp.route('/logout', methods=['POST'])
def logout():
    # Token must be deleted client-side
    response = make_response(jsonify({"message": "You have been logged out."}), 200)
    return response
