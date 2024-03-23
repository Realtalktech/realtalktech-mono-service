# utils/user.py
from flask import jsonify
from rtt_data_app.app import db
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest, Unauthorized, InternalServerError
from email_validator import validate_email, EmailNotValidError
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import pymysql
import pymysql.cursors
import re
# from rtt_data_app.utils import DBManager
from rtt_data_app.models.user import User as model
from rtt_data_app.models import UserDiscussCategory, DiscussCategory, InterestArea
from rtt_data_app.models import UserInterestArea, UserPublicVendor, PublicVendor
from rtt_data_app.models import UserIndustry, Industry, UserPublicVendorEndorsement
from rtt_data_app.auth import Authorizer
from sqlalchemy import exc, func
import logging

class User:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def __fetch_login_credentials_by_username(self, username:str) -> Optional[Dict[str, Optional[str]]]:
        # Database lookup to find a user by username
        user:model = model.query.filter_by(username=username).first()
        if user is None:
            return None
        else:
            return {'user_id': user.id, 'password': user.password}

    def __is_email(self, entered_username:str) -> bool:
        return re.match(r"[^@]+@[^@]+\.[^@]+", entered_username)
    
    def __fetch_username_from_email(self, email:str) -> str:
        user:model = model.query.filter_by(email=email).first()
        if user is None:
            raise Unauthorized("Invalid Email")
        else:
            return user.username

    def __get_user_tech_stack(self, user_id:int) -> List[Dict[str, int | str]]:
        # Database lookup to find tech_stack (UserPublicVendor)
        
        # Query UserPublicVendor to get all vendor_ids associated with user
        user_vendors = db.session.query(UserPublicVendor.vendor_id).filter_by(user_id=user_id).all()
        vendor_ids = [vendor.vendor_id for vendor in user_vendors]

        # Get vendor_names based on vendor_ids
        if vendor_ids:  # Check if the list is not empty
            vendors = db.session.query(PublicVendor.id, PublicVendor.vendor_name).filter(PublicVendor.id.in_(vendor_ids)).all()
            tech_stack = [{'id': vendor.id, 'name': vendor.vendor_name} for vendor in vendors]
        else:
            tech_stack = []

        return tech_stack

    def __get_user_industry_involvement(self, user_id:int)  -> List[Dict[str, int | str]]:
        # Query UserIndustry to get all industry_ids associated with user
        user_industries = db.session.query(UserIndustry.industry_id).filter_by(user_id=user_id).all()
        industry_ids = [industry.industry_id for industry in user_industries]

        # Get industry names based on the industry_ids
        if industry_ids: 
            industries = db.session.query(Industry.id, Industry.industry_name).filter(Industry.id.in_(industry_ids)).all()
            industry_involvement = [{'id': industry.id, 'name': industry.industry_name} for industry in industries]
        else:
            industry_involvement = []

        return industry_involvement

    def __get_user_subscribed_discuss_categories(self, user_id:int) -> List[Dict[str, int | str]]:
        # Database lookup to find subscribed discuss categories (categories of work)
        # Query to get all category_ids associated with the user
        user_categories = db.session.query(UserDiscussCategory.category_id).filter_by(user_id=user_id).all()
        category_ids = [category.category_id for category in user_categories]

        # Now, get the category names based on the category_ids
        if category_ids:
            categories = db.session.query(DiscussCategory.id, DiscussCategory.category_name).filter(DiscussCategory.id.in_(category_ids)).all()
            subscribed_discuss_categories = [{'id': category.id, 'name': category.category_name} for category in categories]
        else:
            subscribed_discuss_categories = []

        return subscribed_discuss_categories
    
    def __get_user_interest_areas(self, user_id:int) -> List[Dict[str, int | str]]:
        # Query to find interest areas associated with the user
        user_interest_areas = db.session.query(UserInterestArea.interest_area_id).filter_by(user_id=user_id).all()
        interest_area_ids = [area.interest_area_id for area in user_interest_areas]

        if interest_area_ids:
            interest_areas = db.session.query(InterestArea.id, InterestArea.interest_area_name).filter(InterestArea.id.in_(interest_area_ids)).all()
            interest_areas_list = [{'id': area.id, 'name': area.interest_area_name} for area in interest_areas]
        else:
            interest_areas_list = []

        return interest_areas_list

    def __get_user_details(self, user_id:int, is_owner:bool) -> Dict[str, int | str]:
        user:model = model.query.filter_by(id=user_id).first()
        if is_owner:
            user_details = {
                'id': user.id,
                'fullname': user.full_name,
                'username': user.username,
                'currentCompany': user.current_company,
                'email': user.email,
                'linkedinUrl': user.linkedin_url,
                'bio': user.bio,
                'accountCreationTime': user.creation_time.isoformat(),
                'accountUpdateTime': user.update_time.isoformat()
            }
            
        else:
            user_details = {
                'fullname': user.full_name,
                'username': user.username,
                'currentCompany': user.current_company,
                'linkedinUrl': user.linkedin_url,
                'bio': user.bio
            }

        return user_details          

    def __validate_signup_fields(self, data:dict) -> List[str]:
        full_name = data.get('fullname')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        current_company = data.get('currentCompany')

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
        
        return missing_fields

    def __extract_signup_fields(self, data:dict) -> Tuple[Optional[str], Optional[str], Optional[str], 
                                                                                               Optional[str], List[int], Optional[str], 
                                                                                               List[int], List[int], List[int], 
                                                                                               Optional[str], Optional[str]]:
        full_name = data.get('fullname')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        tech_stack = data.get('techstack', [])  # List of vendor ids from "setup your profile"
        current_company = data.get('currentCompany')
        industry_involvement = data.get('industryInvolvement', []) # List of "what industry are you in?" ids
        categories_of_work = data.get('workCategories', []) # List of "what do you do?" ids
        linkedin_url = data.get('linkedinUrl')
        bio = data.get('bio')
        interest_areas = data.get('interestAreas', []) # List of interest area ids
        
        return (full_name, username, email, 
                password, tech_stack, current_company, industry_involvement, 
                categories_of_work, interest_areas, linkedin_url, bio)

    def __create_user_and_fetch_id(self, full_name:str, username:str, email:str, 
                                   password:str, current_company:str, linkedin_url:str, bio:str) -> int:
        hashed_password = generate_password_hash(password)
        new_user = model(
            full_name=full_name,
            username=username,
            email=email,
            current_company=current_company,
            linkedin_url=linkedin_url or '',
            bio=bio or '',
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return new_user.id  # ID of the newly created User
    
    def __set_user_subscribed_discuss_categories(self, user_id:int, subscribed_discuss_category_ids:List[int]) -> None:
        # Link categories of work to User in UserDiscussCategory for feed population
        for category_id in subscribed_discuss_category_ids:
            new_category_link = UserDiscussCategory(user_id=user_id, category_id=category_id)
            db.session.add(new_category_link)
        db.session.commit()
        
    def __set_user_interest_areas(self, user_id:int, interest_area_ids:List[int]) -> None:
        # Link interest areas to user
        for area_id in interest_area_ids:
            new_interest_area_link = UserInterestArea(user_id=user_id, interest_area_id=area_id)
            db.session.add(new_interest_area_link)
        db.session.commit()
    
    def __set_user_industry_involvement(self, user_id:int, industry_involvement_ids:List[int]) -> None:
        # Link industry involvement to user
        for industry_id in industry_involvement_ids:
            new_industry_link = UserIndustry(user_id=user_id, industry_id=industry_id)
            db.session.add(new_industry_link)
        db.session.commit()
    
    def __set_user_tech_stack(self, user_id:int, tech_stack_vendor_names:List[str]) -> None:
        # Link tech stack to user
        for vendor_name in tech_stack_vendor_names:
            # Ensure the vendor exists, add if not
            existing_vendor = PublicVendor.query.filter_by(vendor_name=vendor_name).first()
            if existing_vendor is None:  # If the vendor doesn't exist, add it to the table
                new_vendor = PublicVendor(vendor_name=vendor_name)
                db.session.add(new_vendor)
                existing_vendor = new_vendor
            # Associate user with vendor
            new_tech_link = UserPublicVendor(user_id=user_id, vendor_id=existing_vendor.id)
            db.session.add(new_tech_link)
        db.session.commit()

    def __get_user_techstack_endorsements(self, user_id:int, requester_id:int, 
                                          tech_stack:List[Dict[str, int | str]]) -> Dict[str, int | str | bool]:
        # Process associated vendors from tech_stack and check endorsements
        vendors_with_endorsements = []
        if user_id == requester_id:
            for item in tech_stack:
                all_endorsements = self.__get_all_endorsements_from_id(item['id'], user_id)
                vendors_with_endorsements.append({
                    'id': item['id'],
                    'name': item['name'],
                    'totalEndorsements': self.__get_total_endorsements_from_id(item['id'], user_id),
                    'userEndorsements': all_endorsements
                })
        else:
            for item in tech_stack:
                endorsement = self.__check_endorsement_from_id(item['id'], user_id, requester_id)
                vendors_with_endorsements.append({
                    'id': item['id'],
                    'name': item['name'],
                    'totalEndorsements': self.__get_total_endorsements_from_id(item['id'], user_id),
                    'endorsedByRequester': endorsement
                })
        return vendors_with_endorsements

    def __check_endorsement_from_id(self, vendor_id:int, user_id:int, requester_id:int):
        """Check if requester has endorsed user for a particular vendor"""
        # Using count() is more efficient than loading objects when you only need the count
        count = UserPublicVendorEndorsement.query.filter_by(
            endorser_user_id=requester_id,
            endorsee_user_id=user_id,
            vendor_id=vendor_id
        ).count()
        return count > 0

    def __get_all_endorsements_from_id(self, vendor_id:int, user_id:int) -> List[Dict[str, int | str]]:
        """Get all users who have endorsed (user_id) in a particular skill (vendor)"""
        endorsements = UserPublicVendorEndorsement.query.filter_by(
            endorsee_user_id=user_id,
            vendor_id=vendor_id
        ).all()

        users_with_endorsement = [{
            'id': endorsement.endorser.id,
            'username': endorsement.endorser.username
        } for endorsement in endorsements]
        return users_with_endorsement

    def __get_total_endorsements_from_id(self, vendor_id:int, user_id:int) -> int:
        return UserPublicVendorEndorsement.query.filter_by(
            vendor_id=vendor_id,
            endorsee_user_id=user_id
        ).count()

    def authenticate_returning_user(self, entered_username:str, entered_password:str):
        if self.__is_email(entered_username):
            # If attempting to login via email, validate and fetch username
            email = entered_username
            try:
                email_info = validate_email(email, check_deliverability=False)
                email = email_info.normalized
            except EmailNotValidError as e:
                raise BadRequest(str(e))
            # Will raise error if email is not found
            entered_username = self.__fetch_username_from_email(email)
        try:
            user_data = self.__fetch_login_credentials_by_username(entered_username)
            if user_data is None:
                raise Unauthorized("Invalid Username")

            if not check_password_hash(user_data.get('password'), entered_password):
                raise Unauthorized("Incorrect Password")
            
            # Authorized, generate token
            user_id = user_data.get('user_id')
            token = Authorizer.generate_token(user_id)
            
            # Grab user details
            user_details = self.__get_user_details(user_id, True)
            tech_stack = self.__get_user_tech_stack(user_id)
            industry_involvement = self.__get_user_industry_involvement(user_id)
            subscribed_discuss_categories = self.__get_user_subscribed_discuss_categories(user_id)
            interest_areas = self.__get_user_interest_areas(user_id)

            user_details['occupationalAreas'] = subscribed_discuss_categories
            user_details['industryInvolvement'] = industry_involvement
            user_details['techstack'] = tech_stack
            user_details['interestAreas'] = interest_areas

            return jsonify(
                {
                    "message": "Login successful",
                    'userDetails': user_details,
                    "token": token
                }
            ), 200

        except exc.SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(str(e))
            raise InternalServerError(f"Database error: {str(e)}")

        finally:
            db.session.close()
    
    def get_user_public_profile(self, user_id:int, requester_id:int):
        try:
            user_details = self.__get_user_details(user_id, False)
            tech_stack = self.__get_user_tech_stack(user_id)
            vendors_with_endorsements = self.__get_user_techstack_endorsements(user_id, requester_id, tech_stack)
            response = {
                'userDetails': user_details,
                'vendors': vendors_with_endorsements
            }
            return jsonify(response)
        except exc.SQLAlchemyError as e:
            self.logger.error(str(e))
            raise InternalServerError(str(e))
        finally:
            db.session.commit()
            db.session.close()
    
    def get_user_private_profile(self, user_id:int):
        try:
            user_details = self.__get_user_details(user_id, True)
            tech_stack = self.__get_user_tech_stack(user_id)
            vendors_with_endorsements = self.__get_user_techstack_endorsements(user_id, user_id, tech_stack)
            response = {
                'userDetails': user_details,
                'vendors': vendors_with_endorsements
            }
            return jsonify(response)
        except exc.SQLAlchemyError as e:
            self.logger.error(str(e))
            raise InternalServerError(str(e))
        finally:
            db.session.commit()
            db.session.close()

    def signup(self, data:dict):
        # Extract data from request
        missing_fields = self.__validate_signup_fields(data)
        
        # Raise error if any fields are missing
        if len(missing_fields) > 0:
            missing_fields_str = missing_fields_str = ', '.join(missing_fields)  # Convert the list to a comma-separated string
            error_message = f"Missing required fields: {missing_fields_str}"
            raise BadRequest(error_message)
        
        (full_name, username, email, password, tech_stack_names, 
        current_company, industry_involvement_ids, subscribed_discuss_categories_ids, 
        interest_area_ids, linkedin_url, bio) = self.__extract_signup_fields(data)

        # Raise error if not in standard email format
        try:
            email_info = validate_email(email, check_deliverability=True)
            # replace with normalized form
            email = email_info.normalized
        except EmailNotValidError as e:
            raise BadRequest(str(e))
        
        # Create new user
        try:
            user_id = self.__create_user_and_fetch_id(full_name, username, 
                             email, password, current_company, 
                             linkedin_url, bio)
            self.__set_user_subscribed_discuss_categories(user_id, subscribed_discuss_categories_ids)
            self.__set_user_interest_areas(user_id, interest_area_ids)
            self.__set_user_industry_involvement(user_id, industry_involvement_ids)
            self.__set_user_tech_stack(user_id, tech_stack_names)

            token = Authorizer.generate_token(user_id)
            response = jsonify(
                    {
                        "message": "Signup successful",
                        "token": token
                    }
                ), 201
            return response

        except exc.SQLAlchemyError as e:
            self.logger.error(str(e))
            raise InternalServerError(str(e))
        finally:
            db.session.commit()
            db.session.close()
        
    def convert_username_to_id(self,username:str)->int:
        user = model.query.filter_by(username=username).first()
        try:
            return user.id
        except AttributeError as e:
            self.logger.error(f"User with username {username} not found")
            raise BadRequest(f"User with username {username} not found")
        finally:
            db.session.close()

    def edit_profile(self, user_id: int, 
                    new_full_name: str = None, 
                    new_email: str = None, 
                    new_bio: str = None, 
                    new_linkedin: str = None, 
                    new_tech_stack_names: list = None,
                    new_company: str = None):
        try:
            user = model.query.filter_by(id=user_id).one()

            if new_full_name:
                user.full_name = new_full_name
            if new_email:
                user.email = new_email
            if new_bio:
                user.bio = new_bio
            if new_linkedin:
                user.linkedin_url = new_linkedin
            if new_company:
                user.current_company = new_company

            user.update_time = func.now()

            db.session.commit()
            
            if new_tech_stack_names is not None:
                # Get current user's tech stack names
                current_tech_stack = self.__get_user_tech_stack(user.id)
                current_tech_stack = [name['name'] for name in current_tech_stack]
                
                # Find vendors to add
                for tech_name in set(new_tech_stack_names) - set(current_tech_stack):
                    vendor = PublicVendor.query.filter_by(vendor_name=tech_name).first()

                    if not vendor:
                        vendor = PublicVendor(vendor_name=tech_name)
                        db.session.add(vendor)
                        vendor = PublicVendor.query.filter_by(vendor_name=tech_name).first()
                    
                    tech_stack_addition = UserPublicVendor(user_id=user.id, vendor_id=vendor.id)
                    db.session.add(tech_stack_addition)
                
                # Find vendors to remove
                for tech_name in set(current_tech_stack) - set(new_tech_stack_names):
                    vendor = PublicVendor.query.filter_by(vendor_name=tech_name).first()
                    if vendor:
                        UserPublicVendor.query.filter_by(user_id=user.id, vendor_id=vendor.id).delete()
                        # Remove all endorsements associated with the removed tech stack vendor
                        # UserPublicVendorEndorsement.query.filter_by(endorsee_user_id=user_id, vendor_id=vendor.id).delete()

        except exc.SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(str(e))
            raise InternalServerError(f"Database error: {str(e)}")

    def edit_password(self, user_id: int, old_password: str, new_password: str):
        try:
            # Fetch the current user
            user = model.query.filter_by(id=user_id).first()

            if user and check_password_hash(user.password, old_password):
                # If the old password is correct, update with the new hashed password
                user.password = generate_password_hash(new_password)
                db.session.commit()
            else:
                # Raise an exception if the old password is incorrect
                raise BadRequest("error: Old Password is Incorrect")
        except exc.SQLAlchemyError as e:
            # Log and raise an internal server error
            self.logger.error(f"SQLAlchemy Error: {e}")
            db.session.rollback()  # Rollback the session in case of error
            raise InternalServerError("An error occurred while updating the password.")      

    def endorse_user(self, user_id:int, endorsee_user_id:int, vendor_id:int):
        try:
            temp = model.query.filter_by(id=endorsee_user_id).first()
            temp.id
        except AttributeError as e:
            self.logger.error(str(e))
            raise BadRequest("Endorsee does not exist!")
        
        try:
            vendor = UserPublicVendor.query.filter_by(user_id=endorsee_user_id, vendor_id=vendor_id).first()
            vendorid = vendor.vendor_id
        except AttributeError as e:
            self.logger.error(str(e))
            raise BadRequest("User does not have vendor in their techstack")

        try:
            endorsement = UserPublicVendorEndorsement(
                endorser_user_id=user_id,
                endorsee_user_id=endorsee_user_id,
                vendor_id=vendor_id
            )
            db.session.add(endorsement)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()  # Rollback the transaction if there's an error
            self.logger.error(f"SQLAlchemy Error: {e}")
            raise InternalServerError("An error occurred while adding the endorsement.")
    
    def get_onboarding_information(self):
        try:
            # Query all interest areas
            interest_areas = InterestArea.query.with_entities(InterestArea.id, InterestArea.interest_area_name).all()
            interest_areas_list = [{'id': area.id, 'interest_area_name': area.interest_area_name} for area in interest_areas]
            
            # Query all industries
            industries = Industry.query.with_entities(Industry.id, Industry.industry_name).all()
            industries_list = [{'id': industry.id, 'industry_name': industry.industry_name} for industry in industries]
            
            # Query all discussion categories
            subscription_areas = DiscussCategory.query.with_entities(DiscussCategory.id, DiscussCategory.category_name).all()
            subscription_areas_list = [{'id': category.id, 'category_name': category.category_name} for category in subscription_areas]
            
            # Query all public vendors (tech stack)
            tech_stack = PublicVendor.query.with_entities(PublicVendor.id, PublicVendor.vendor_name).all()
            tech_stack_list = [{'id': vendor.id, 'vendor_name': vendor.vendor_name} for vendor in tech_stack]

            # Combine the data into a JSON response
            return jsonify({
                'interestAreas': interest_areas_list,
                'industries': industries_list,
                'subscriptionAreas': subscription_areas_list,
                'techstack': tech_stack_list
            })
        except exc.SQLAlchemyError as e:
            self.logger.error(str(e))
            raise InternalServerError("Error fetching onboarding.")
    
    def check_username_availability(self, username):
        try:
            user = model.query.filter_by(username=username).first()
        except exc.SQLAlchemyError as e:
            self.logger(str(e))
            raise InternalServerError("An error occured while checking for username availability")
        if user is None:
            return jsonify({
                'message': "Username is available",
                'available': True
            })
        else:
            return jsonify({
                'message': "Username is unavailable",
                'available': False
            })

    def check_email_availability(self, email):
        try:
            user = model.query.filter_by(email=email).first()
        except exc.SQLAlchemyError as e:
            self.logger(str(e))
            raise InternalServerError("An error occured while checking for email availability")
        if user is None:
            return jsonify({
                'message': "Email is available",
                'available': True
            })
        else:
            return jsonify({
                'message': "Email is unavailable",
                'available': False
            })