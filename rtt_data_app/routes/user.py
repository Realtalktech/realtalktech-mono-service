from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
from rtt_data_app.utils.db_manager import DBManager
from werkzeug.exceptions import BadRequest, Unauthorized, InternalServerError
from rtt_data_app.utils import User
from rtt_data_app.auth import token_required

user_bp = Blueprint('user_bp', __name__)
db_manager = DBManager()

@user_bp.route('/user/<requested_username>', methods=['GET'])
@token_required
def get_user_profile_by_username(user_id, requested_username):
    """Get a user's public profile"""
    if not user_id:
        raise Unauthorized("error: User is not authorized") # 401 Unauthorized
    
    # will raise bad request if user is not found
    requested_user_id = User().convert_username_to_id(requested_username)

    is_profile_owner = (user_id == requested_user_id)

    if is_profile_owner:
        return User().get_user_private_profile(requested_user_id)
    else:
        return User().get_user_public_profile(requested_user_id, user_id)

@user_bp.route('/editProfile', methods=['PUT'])
@token_required
def edit_profile(user_id):
    if not user_id:
        raise Unauthorized("error: User is not authorized") # 401 Unauthorized
    
    data:dict = request.json

    new_fullname = data.get('fullname')
    new_email = data.get('email')
    new_tech_stack = data.get('techstack', [])  # List of new vendor names
    new_bio = data.get('bio')
    new_linkedin = data.get('linkedin')
    new_company = data.get('currentCompany')
    user = User()
    user.edit_profile(
        user_id=user_id,
        new_full_name=new_fullname,
        new_tech_stack_names=new_tech_stack,
        new_bio=new_bio,
        new_email=new_email,
        new_linkedin=new_linkedin,
        new_company=new_company
    )

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
    
    user = User()
    user.endorse_user(user_id, endorsee_user_id, vendor_id)
    return jsonify({"message": "Profile endorsed successfully"}), 200

@user_bp.route('/editPassword', methods=['POST'])
@token_required 
def edit_password(user_id):
    # Get JSON data from request
    data = request.get_json()
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')

    if not old_password or not new_password:
        raise BadRequest("error: Missing old or new password")
    
    user = User()
    user.edit_password(user_id, old_password, new_password)
    return jsonify({'message': 'Password updated successfully'}), 200