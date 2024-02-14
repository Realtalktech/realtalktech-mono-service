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
        # requested_user = User.find_by_id(
        #     cursor, user_id = owner_check_user.id, 
        #     needed_info = ['id', 'full_name', 'current_company', 'email', 'linkedin_url', 'bio'],
        #     subscribed_categories=True,
        #     tech_stack=True, interest_areas=True, industry_involvement=True
        # )
    else:
        return requested_user.get_user_public_profile()


    profile_owner_response = {}

    # Fetch onboarding responses if is profile owner
    if is_profile_owner: profile_owner_response = fetch_onboarding_information(requested_user)

    # Process associated vendors from tech_stack and check endorsements
    vendors_with_endorsements = []
    for idx, vendor_id in enumerate(requested_user.tech_stack_vendor_ids):
        # Check for endorsement
        endorsement = User.check_endorsement_from_id(
            vendor_id, requested_user.id, cursor
        )

        vendors_with_endorsements.append({
            'vendorId': vendor_id,
            'vendorName': requested_user.tech_stack_vendor_names[idx],
            'endorsedByRequester': endorsement
        })
    
    cursor.close()
    conn.close()

    if is_profile_owner: #fullname, uername, current_company, email, linkedin_url, bio, creation_time, update_time
        user_details = {
            'fullname': requested_user.full_name,
            'username': requested_user.username,
            'currentCompany': requested_user.current_company,
            'email': requested_user.email,
            'linkedinUrl': requested_user.linkedin_url,
            "bio": requested_user.bio,
            "accountCreationTime": requested_user.fetch_account_creation_time(cursor),
            "accountUpdateTime": requested_user.fetch_account_update_time(cursor)
        }
    else: #fullname, username, current_company, linkedin_url, bio
        user_details = {
            'fullname': requested_user.full_name,
            'username': requested_user.username,
            'currentCompany': requested_user.current_company,
            'linkedinUrl': requested_user.linkedin_url,
            "bio": requested_user.bio
        }

    vendors_with_endorsements = [convert_keys_to_camel_case(item) for item in vendors_with_endorsements]
    if is_profile_owner:
        response = {
            'userDetails': user_details,
            'vendors': vendors_with_endorsements,
            'privateProfile': profile_owner_response
        }
    else:
        response = {
            'userDetails': user_details,
            'vendors': vendors_with_endorsements
        }

    return jsonify(response)

@user_bp.route('/editProfile', methods=['PUT'])
@token_required
def edit_profile(user_id):
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401  # 401 Unauthorized
    
    try:
        new_fullname = data.get('fullname')
        new_email = data.get('email')
        new_tech_stack = set(data.get('techstack', []))  # List of new vendor names
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        user = User.find_by_id(cursor, user_id=user_id)
        data = request.json
        user.edit_profile(cursor, new_fullname, new_email, new_tech_stack)
        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Profile updated successfully"}), 200


@user_bp.route('/endorse', methods = ['PUT'])
@token_required
def endorse_user(user_id):
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401  # 401 Unauthorized
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    try:
        data = request.json
        endorsee_username = data.get('endorseeUsername')
        vendor_id = data.get('vendorId')

        if not(endorsee_username and vendor_id):
            return jsonify({"error": "Endorsee User Id, Vendor Id is required"}), 400

        endorsed_user = User.find_by_username(
            cursor, 
            username=endorsee_username, 
            needed_info=['id']
        )
        endorsed_user.receive_endorsement(vendor_id, user_id, cursor)
        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Profile endorsed successfully"}), 200

