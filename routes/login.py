from flask import Blueprint, jsonify, request, make_response
import pymysql
import pymysql.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest
from auth import Authorizer
from models import User
from models import SandUser
from utils import DBManager

login_bp = Blueprint('login_bp', __name__)
db_manager = DBManager()

@login_bp.route('/signup', methods=['PUT'])
def signup():
    # Extract data
    data = request.json
    user = SandUser()
    return user.signup(data)

@login_bp.route('/login', methods=['POST'])
def login():
    # Extract username and password from the request
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        raise BadRequest("Username and password are required")
    
    user = SandUser()
    return user.authenticate_returning_user(username, password)

@login_bp.route('/logout', methods=['POST'])
def logout():
    # Token must be deleted client-side
    response = make_response(jsonify({"message": "You have been logged out."}), 200)
    return response
