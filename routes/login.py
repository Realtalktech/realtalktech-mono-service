from flask import Blueprint, jsonify, request, make_response
import pymysql
import pymysql.cursors
from werkzeug.exceptions import BadRequest
from auth import Authorizer
from utils import User
from utils import DBManager

login_bp = Blueprint('login_bp', __name__)
db_manager = DBManager()

@login_bp.route('/signup', methods=['PUT'])
def signup():
    # Extract data
    data = request.json
    return User().signup(data)

@login_bp.route('/login', methods=['POST'])
def login():
    # Extract username/email and password from the request
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        raise BadRequest("Username/Email and password are required")
    
    return User().authenticate_returning_user(username, password)

@login_bp.route('/logout', methods=['POST'])
def logout():
    # Token must be deleted client-side
    response = make_response(jsonify({"message": "You have been logged out."}), 200)
    return response

@login_bp.route('/onboard')
def get_interest_areas():
    conn = db_manager.get_db_connection()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
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