from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
from utils.db_manager import DBManager
from werkzeug.exceptions import BadRequest, Unauthorized, InternalServerError
from utils.responseFormatter import convert_keys_to_camel_case
from models import User, SandUser
from utils import token_required

user_bp = Blueprint('user_bp', __name__)
db_manager = DBManager()

@user_bp.route('/user/<requested_username>', methods=['GET'])
@token_required
def get_user_profile_by_username(user_id, requested_username):
    """Get a user's public profile"""
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401  # 401 Unauthorized
    
    requested_user = SandUser()
    try:
        requested_user_id = requested_user.convert_username_to_id(requested_username)
    except pymysql.MySQLError as e:
        requested_user.conn.rollback()
        raise InternalServerError(f"Database error: {str(e)}")

    if requested_user_id is None:
        raise BadRequest(f"Username {requested_username} not found")

    is_profile_owner = (user_id == requested_user_id)

    if is_profile_owner:
        return requested_user.get_user_private_profile()
    else:
        return requested_user.get_user_public_profile()

@user_bp.route('/editProfile', methods=['PUT'])
@token_required
def edit_profile(user_id):
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401  # 401 Unauthorized
    
    data = request.json

    new_fullname = data.get('fullname')
    new_email = data.get('email')
    new_tech_stack = set(data.get('techstack', []))  # List of new vendor names
    new_bio = data.get('bio')
    new_linkedin = data.get('linkedin')
    new_company = data.get('new_company')
    user = SandUser()
    user.new_edit_profile(user_id, new_fullname, new_email, 
                          new_tech_stack, new_bio, new_linkedin, new_company)

    return jsonify({"message": "Profile updated successfully"}), 200


@user_bp.route('/endorse', methods = ['PUT'])
@token_required
def endorse_user(user_id):
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401  # 401 Unauthorized

    data = request.json
    endorsee_user_id= data.get('endorseeUserId')
    vendor_id = data.get('vendorId')

    if not(endorsee_user_id and vendor_id):
        raise BadRequest("Endorsee User Id, Vendor Id is required")
    
    user = SandUser()
    user.endorse_user(user_id, endorsee_user_id, vendor_id)
    return jsonify({"message": "Profile endorsed successfully"}), 200

