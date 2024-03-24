from flask import Blueprint, jsonify, request, make_response
from werkzeug.exceptions import BadRequest
from rtt_data_app.utils import User

login_bp = Blueprint('login_bp', __name__)

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

@login_bp.route('/onboard', methods=['GET'])
def get_onboarding():
    return User().get_onboarding_information()

@login_bp.route('/user/check', methods=['GET'])
def check():
    email = request.args.get('email', type=str)
    username = request.args.get('username', type=str)
    if username is not None:
        return User().check_username_availability(username)
    else:
        return User().check_email_availability(email)