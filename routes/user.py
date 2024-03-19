from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
import requests
from utils.db_manager import DBManager
from utils.responseFormatter import convert_keys_to_camel_case
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from utils import token_required
import os

user_bp = Blueprint('user_bp', __name__)
db_manager = DBManager()

def fetch_onboarding_information(user: User):
    """Fetch onboarding information for profile private view."""
    industries = []
    for idx,industry_name in enumerate(user.industry_involvement_names):
        industries.append({
            'id': user.industry_involvement_ids[idx],
            'name': industry_name
        })
   
    interest_areas = []
    for idx, interest_area_name in enumerate(user.interest_area_names):
        interest_areas.append({
            'id': user.interest_area_ids[idx],
            'name': interest_area_name
        })
    
    subscribed_discussion_categories = []
    for idx, subscribed_category_name in enumerate(user.subscribed_discuss_category_names):
        subscribed_discussion_categories.append({
            'id': user.subscribed_discuss_category_ids[idx],
            'name': subscribed_category_name
        })
    
    # industries = [convert_keys_to_camel_case(thing) for thing in industries]
    # interest_areas = [convert_keys_to_camel_case(thing) for thing in interest_areas]
    # subscribed_discussion_categories = [convert_keys_to_camel_case(thing) for thing in subscribed_discussion_categories]

    return {
        "industryInvolvement": industries,
        "interestAreas": interest_areas,
        "subscribedCategories": subscribed_discussion_categories
    }

@user_bp.route('/user/<requested_username>/check', methods=['GET'])
def check_username(requested_username):
    """Get a user's public profile"""
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()

    owner_check_user = User.find_by_username(
        cursor,
        username=requested_username,
        needed_info=['username'])

    has_username = (owner_check_user != None and owner_check_user.username == requested_username)

    if has_username:
        response = {
            'username': requested_username
        }
    else:
        response = {
            'username': ''
        }
    
    cursor.close()
    conn.close()

    return jsonify(response)

@user_bp.route('/user/check', methods=['GET'])
def check():
    """Get a user's public profile"""
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()

    email = request.args.get('email', type=str)
    username = request.args.get('username', type=str)

    if email != None and email != '':
        found_user = User.find_by_email(
            cursor,
            email=email,
            needed_info=['email'])
        has_email = (found_user != None and found_user.email == email)
        if has_email:
            cursor.close()
            conn.close()
            return jsonify({'available': False})
        # if has_username:
        #     response = {
        #         'username': requested_username
        #     }
        # else:
        #     response = {
        #         'username': ''
        #     }
    if username != None and username != '':
        found_user = User.find_by_username(
            cursor,
            username=username,
            needed_info=['username'])
        has_username = (found_user != None and found_user.username == username)
        if has_username:
            cursor.close()
            conn.close()
            return jsonify({'available': False})

    cursor.close()
    conn.close()
    return jsonify({'available': True})

@user_bp.route('/user/<requested_username>', methods=['GET'])
# @user_bp.route('/user/<requested_username>/<user_id>', methods=['GET'])
@token_required
# def get_user_profile_by_username(user_id, requested_username):
def get_user_profile_by_username(user_id, requested_username):
    """Get a user's public profile"""
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401  # 401 Unauthorized

    owner_check_user = User.find_by_username(
        cursor,
        username=requested_username,
        needed_info=['id'])

    is_profile_owner = (owner_check_user.id == user_id)

    if is_profile_owner:
        requested_user = User.find_by_id(
            cursor, user_id = owner_check_user.id, 
            needed_info = ['id', 'full_name', 'current_company', 'email', 'linkedin_url', 'bio'],
            subscribed_categories=True,
            tech_stack=True, interest_areas=True, industry_involvement=True
        )
    else:
        requested_user = User.find_by_id(
            cursor, user_id = owner_check_user.id, tech_stack=True,
            needed_info=['id', 'full_name', 'username', 'current_company', 'linkedin_url', 'bio']
        )

    profile_owner_response = {}

    # Fetch onboarding responses if is profile owner
    if is_profile_owner: profile_owner_response = fetch_onboarding_information(requested_user)

    # Process associated vendors from tech_stack and check endorsements
    vendors_with_endorsements = []
    for idx, vendor_id in enumerate(requested_user.tech_stack_vendor_ids):
        # Check for endorsement
        # endorsement = User.check_endorsement_from_id(user_id, requested_user.id, cursor)
        endorsement = User.check_endorsement_from_id(vendor_id, user_id, requested_user.id, cursor)
        print("DEB", vendor_id, requested_user.id)
        endorsementCount = User.get_endorsements_count(vendor_id, requested_user.id, cursor)

        vendors_with_endorsements.append({
            'vendorId': vendor_id,
            'vendorName': requested_user.tech_stack_vendor_names[idx],
            'endorsedByRequester': endorsement,
            'endorsementCount': endorsementCount,
        })


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
    
    cursor.close()
    conn.close()

    return jsonify(response)

@user_bp.route('/editProfile', methods=['PUT'])
# @user_bp.route('/editProfile/<user_id>', methods=['PUT'])
@token_required
def edit_profile(user_id):
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401  # 401 Unauthorized
    
    conn = db_manager.get_db_connection()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    data:dict = request.json

    try:
        new_fullname = data.get('fullname')
        new_email = data.get('email')
        new_tech_stack = data.get('techstack', [])  # List of new vendor names
        new_bio = data.get('bio')
        new_linkedin = data.get('linkedin')
        new_company = data.get('company')
        new_username = data.get('username')
        user = User.find_by_id(cursor, user_id=user_id, needed_info=['id', 'username', 'linkedin_url', 'bio'], tech_stack=True)
        user.edit_profile(cursor, new_fullname, new_email, new_tech_stack, new_bio, new_linkedin, new_company, new_username)
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

@user_bp.route('/editPassword', methods=['POST'])
@token_required 
def edit_password(user_id):
    # Get JSON data from request
    data = request.get_json()
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')

    if not old_password or not new_password:
        return jsonify({'message': 'Missing old or new password'}), 400

    # Connect to the database
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()

    try:
        # Fetch the current user's password
        cursor.execute("SELECT password FROM User WHERE id = %s", (user_id,))
        user_record = cursor.fetchone()

        if user_record and check_password_hash(user_record['password'], old_password):
            # If the old password is correct, update with the new hashed password
            hashed_new_password = generate_password_hash(new_password)
            cursor.execute("UPDATE User SET password = %s WHERE id = %s", (hashed_new_password, user_id))
            conn.commit()
            return jsonify({'message': 'Password updated successfully'}), 200
        else:
            return jsonify({'message': 'Old password is incorrect'}), 401
    except Exception as e:
        return jsonify({'message': 'Error updating password', 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@user_bp.route('/contactus', methods=['POST'])
@token_required 
def edit_password(user_id):
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')
    username = data.get('username')
    emailId = data.get('emailId')

    # Prepare the payload for Slack
    slack_message = {
        'text': f"New message from {name}:\nEmail: {email}\nUsername: {username}\nEmail ID: {emailId}\nMessage: {message}"
    }

    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    # Post the message to Slack
    response = requests.post(webhook_url, json=slack_message)

    # Return the response to the client
    return jsonify({'status': 'sent', 'response': response.text}), response.status_code
