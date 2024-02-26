# models/user.py
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest, Unauthorized, InternalServerError
from email_validator import validate_email, EmailNotValidError
from typing import Optional, Dict, List, Tuple, Union
from datetime import datetime
import pymysql
import pymysql.cursors
import re
from utils import DBManager
from auth import Authorizer
import logging


class User:
    def __init__(self):
        self.db_manager = DBManager()
        self.conn = self.db_manager.get_db_connection()
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
        self.logger = logging.getLogger(__name__)
    
    def __fetch_login_credentials_by_username(self, username:str) -> Optional[Dict[str, Optional[str]]]:
        # Database lookup to find a user by username
        self.cursor.execute(f"SELECT id, password FROM User WHERE username = %s", (username))
        user_data = self.cursor.fetchone()
        if not user_data:
            return None
        else:
            return {'user_id': user_data.get('id'), 'password': user_data.get('password')}

    def __fetch_account_creation_time(self, user_id:int) -> Optional[str]:
        self.cursor.execute("""SELECT creation_time FROM User WHERE id=%s""",(user_id))
        creation_time:datetime = self.cursor.fetchone().get('creation_time')
        creation_time = creation_time.isoformat()
        return creation_time
    
    def __fetch_account_update_time(self, user_id:int) -> Optional[str]:
        self.cursor.execute("""SELECT update_time FROM User WHERE id=%s""",(user_id))
        update_time:datetime = self.cursor.fetchone().get('update_time')
        update_time = update_time.isoformat()
        return update_time

    def __is_email(self, entered_username:str) -> bool:
        return re.match(r"[^@]+@[^@]+\.[^@]+", entered_username)
    
    def __fetch_username_from_email(self, email:str) -> str:
        self.cursor.execute("""SELECT username FROM User WHERE email = %s""",(email,))
        username = self.cursor.fetchone()
        if not username:
            raise Unauthorized("Invalid Email")
        else:
            return username.get('username')

    def __get_user_tech_stack(self, user_id:int) -> List[Dict[str, int | str]]:
        # Database lookup to find tech_stack (UserPublicVendor)
        self.cursor.execute(
            """SELECT vendor_id FROM UserPublicVendor WHERE user_id = %s""",
            (user_id)
        )
        user_skills = self.cursor.fetchall()
        tech_stack_vendor_names = []
        tech_stack_vendor_ids = []

        for skill in user_skills:
            self.cursor.execute(
                """SELECT vendor_name FROM PublicVendor WHERE id = %s""",
                (skill['vendor_id'])
            )
            tech_stack_vendor_name = self.cursor.fetchone()['vendor_name']
            tech_stack_vendor_names.append(tech_stack_vendor_name)
            tech_stack_vendor_ids.append(skill['vendor_id'])
        
        tech_stack = []
        for idx, name in enumerate(tech_stack_vendor_names):
            tech_stack.append({
                'id': tech_stack_vendor_ids[idx],
                'name': name
            })
        
        return tech_stack

    def __get_user_industry_involvement(self, user_id:int)  -> List[Dict[str, int | str]]:
        # Database lookup to find industry involvement
        self.cursor.execute(
            """SELECT industry_id FROM UserIndustry WHERE user_id = %s""",
            (user_id)
        )
        user_industries = self.cursor.fetchall()
        industry_involvement_names = []
        industry_involvement_ids = []

        for industry in user_industries:
            self.cursor.execute(
                """SELECT industry_name FROM Industry WHERE id = %s""",
                (industry['industry_id'])
            )
            industry_name = self.cursor.fetchone()['industry_name']
            industry_involvement_names.append(industry_name)
            industry_involvement_ids.append(industry['industry_id'])
        
        industry_involvement = []
        for idx, name in enumerate(industry_involvement_names):
            industry_involvement.append({
                'id': industry_involvement_ids[idx],
                'name': name
            })
        
        return industry_involvement

    def __get_user_subscribed_discuss_categories(self, user_id:int) -> List[Dict[str, int | str]]:
        # Database lookup to find subscribed discuss categories (categories of work)
        self.cursor.execute(
            """SELECT category_id FROM UserDiscussCategory WHERE user_id = %s""",
            (user_id)
        )
        discuss_categories = self.cursor.fetchall()
        subscribed_discuss_category_names = []
        subscribed_discuss_category_ids = []
        for category in discuss_categories:
            self.cursor.execute(
                """SELECT category_name FROM DiscussCategory WHERE id = %s""",
                (category['category_id'])
            )
            category_name = self.cursor.fetchone()['category_name']
            subscribed_discuss_category_names.append(category_name)
            subscribed_discuss_category_ids.append(category['category_id'])

        subscribed_discuss_categories = []
        for idx, name in enumerate(subscribed_discuss_category_names):
            subscribed_discuss_categories.append({
                'id': subscribed_discuss_category_ids[idx],
                'name': name
            })

        return subscribed_discuss_categories        

    def __get_user_interest_areas(self, user_id:int) -> List[Dict[str, int | str]]:
        # Database lookup to find interest area names and ids
        self.cursor.execute(
            """SELECT interest_area_id FROM UserInterestArea WHERE user_id = %s""",
            (user_id)
        )
        interest_area_objs = self.cursor.fetchall()
        interest_area_names = []
        interest_area_ids = []

        for area in interest_area_objs:
            self.cursor.execute(
                """SELECT interest_area_name FROM InterestArea WHERE id = %s""",
                (area['interest_area_id'])
            )
            interest_area_name = self.cursor.fetchone()['interest_area_name']
            interest_area_names.append(interest_area_name)
            interest_area_ids.append(area['interest_area_id'])

        interest_areas = []
        for idx, name in enumerate(interest_area_names):
            interest_areas.append({
                'id': interest_area_ids[idx],
                'name': name
            })
        
        return interest_areas

    def __get_user_details(self, user_id:int, is_owner:bool) -> Dict[str, int | str]:
        if is_owner:
            self.cursor.execute("""SELECT id, full_name, username, current_company, email, linkedin_url, bio FROM User WHERE id = %s""", (user_id))
            userObj:dict = self.cursor.fetchone()
            user_details = {
                'id': userObj.get('id'),
                'fullName': userObj.get('full_name'),
                'username': userObj.get('username'),
                'currentCompany': userObj.get('current_company'),
                'email': userObj.get('email'),
                'linkedinUrl': userObj.get('linkedin_url'),
                'bio': userObj.get('bio'),
                'accountCreationTime': self.__fetch_account_creation_time(user_id),
                'accountUpdateTime': self.__fetch_account_update_time(user_id)
            }
        else:
            self.cursor.execute("""SELECT full_name, username, current_company, linkedin_url, bio FROM User WHERE id = %s""", (user_id))
            userObj:dict = self.cursor.fetchone()
            user_details = {
                'fullName': userObj.get('full_name'),
                'username': userObj.get('username'),
                'currentCompany': userObj.get('current_company'),
                'linkedinUrl': userObj.get('linkedin_url'),
                'bio': userObj.get('bio')
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
        tech_stack = data.get('techStack', [])  # List of vendor ids from "setup your profile"
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
        # Hash the password
        hashed_password = generate_password_hash(password)

        values_to_insert = (
            full_name,  # NOT NULL in DB schema
            username,  # NOT NULL in DB schema
            current_company,  # NOT NULL in DB schema
            email,  # NOT NULL in DB schema
            linkedin_url or '',  # Replaces None with empty string
            bio or '',  # Replaces None with empty string
            hashed_password  # NOT NULL in DB schema
        )

        # Insert user into database
        self.cursor.execute("""
            INSERT INTO User (full_name, username, current_company, email, linkedin_url, bio, password) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, values_to_insert)

        user_id = self.cursor.lastrowid # Get ID of newly inserted user
        return user_id
    
    def __set_user_subscribed_discuss_categories(self, user_id:int, subscribed_discuss_category_ids:List[int]) -> None:
        # Link categories of work to User in UserDiscussCategory for feed population
        for discuss_category in subscribed_discuss_category_ids:
            self.cursor.execute("""INSERT INTO UserDiscussCategory (user_id, category_id) VALUES (%s, %s)""",
                            (user_id, discuss_category))
    
    def __set_user_interest_areas(self, user_id:int, interest_area_ids:List[int]) -> None:
        # Link interest areas to user
        for area in interest_area_ids:
            self.cursor.execute(
                """INSERT INTO UserInterestArea (user_id, interest_area_id) VALUES (%s, %s)""",
                                (user_id, area)
                            )     
    
    def __set_user_industry_involvement(self, user_id:int, industry_involvement_ids:List[int]) -> None:
        # Link industry involvement to user
        for industry in industry_involvement_ids:
            self.cursor.execute("""INSERT INTO UserIndustry (user_id, interest_area_id) VALUES (%s, %s)""",
                            (user_id, industry))
    
    def __set_user_tech_stack(self, user_id:int, tech_stack_vendor_names:List[str]) -> None:
        # Link tech stack to user
        for tech in tech_stack_vendor_names:
            self.cursor.execute("SELECT id FROM PublicVendor WHERE vendor_name = %s", (tech,))
            vendor = self.cursor.fetchone()
            if not vendor:
                self.cursor.execute("INSERT INTO PublicVendor (vendor_name) VALUES(%s)", (tech,))
                vendor['id'] = self.cursor.lastrowid

            self.cursor.execute("""
                INSERT INTO UserPublicVendor (user_id, vendor_id) 
                VALUES (%s, %s)
            """, (user_id, vendor['id']))

    def __get_user_techstack_endorsements(self, user_id:int, requester_id:int, 
                                          tech_stack:List[Dict[str, int | str]]) -> Dict[str, int | str | bool]:
        # Process associated vendors from tech_stack and check endorsements
        vendors_with_endorsements = []
        if user_id == requester_id:
            for item in tech_stack:
                all_endorsements = self.__get_all_endorsements_from_id(item['id'], user_id)
                vendors_with_endorsements.append({
                    'vendorId': item['id'],
                    'vendorName': item['name'],
                    'totalEndorsements': self.__get_total_endorsements_from_id(item['id'], user_id),
                    'userEndorsements': all_endorsements
                })
        else:
            for item in tech_stack:
                endorsement = self.__check_endorsement_from_id(item['id'], user_id, requester_id)
                vendors_with_endorsements.append({
                    'vendorId': item['id'],
                    'vendorName': item['name'],
                    'totalEndorsements': self.__get_total_endorsements_from_id(item['id'], user_id),
                    'endorsedByRequester': endorsement
                })
            return vendors_with_endorsements

    def __check_endorsement_from_id(self, vendor_id:int, user_id:int, requester_id:int):
        # Check for endorsement
        self.cursor.execute("""
            SELECT COUNT(*) AS endorsement_count
            FROM UserPublicVendorEndorsement
            WHERE endorser_user_id = %s AND endorsee_user_id = %s AND vendor_id = %s
        """, (requester_id, user_id, vendor_id))
        endorsement = self.cursor.fetchone().get('endorsement_count') > 0
        return endorsement

    def __get_all_endorsements_from_id(self, vendor_id:int, user_id:int) -> List[Dict[str, int | str]]:
        # Get all users who have endorsed (user_id) in a particular skill (vendor)
        users_with_endorsement = []
        self.cursor.execute(
            """SELECT endorser_user_id FROM UserPublicVendorEndorsement WHERE endorsee_user_id = %s AND vendor_id = %s""",
                            (user_id, vendor_id))
        endorsing_users = self.cursor.fetchall()
        for user in endorsing_users:
            self.cursor.execute("""SELECT username FROM User WHERE id = %s""", (user.get('endorser_user_id')))
            username = self.cursor.fetchone().get('username')
            user_obj = {
                'id': user.get('endorser_user_id'),
                'username': username
            }
            users_with_endorsement.append(user_obj)
        return users_with_endorsement

    def __get_total_endorsements_from_id(self, vendor_id:int, user_id:int) -> int:
           self.cursor.execute(
               """SELECT COUNT(*) FROM UserPublicVendorEndorsement WHERE vendor_id = %s AND endorsee_user_id = %s""",
               (vendor_id, user_id))
           total_count = self.cursor.fetchone().get('COUNT(*)')
           return total_count

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

            if not check_password_hash(entered_password, user_data.get('password')):
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
            user_details['interest_areas'] = interest_areas

            return jsonify(
                {
                    "message": "Login successful",
                    'userDetails': user_details,
                    "token": token
                }
            )

        except pymysql.MySQLError as e:
            self.conn.rollback()
            self.logger.error(str(e))
            raise InternalServerError(f"Database error: {str(e)}")

        finally:
            self.cursor.close()
            self.conn.close()
    
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
        except pymysql.MySQLError as e:
            self.conn.rollback()
            self.logger.error(str(e))
            raise InternalServerError(f"Database error: {str(e)}")
        finally:
            self.cursor.close()
            self.conn.close()
    
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
        except pymysql.MySQLError as e:
            self.conn.rollback()
            self.logger.error(str(e))
            raise InternalServerError(f"Database error: {str(e)}")
        finally:
            self.cursor.close()
            self.conn.close()

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

        except pymysql.MySQLError as e:
            self.logger.error(str(e))
            self.conn.rollback()
            raise InternalServerError(str(e))
        finally:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
        
    def convert_username_to_id(self,username:str)->int:
        try:
            self.cursor.execute("""SELECT id FROM User WHERE username = %s""", username)
            user_obj = self.cursor.fetchone()
            return user_obj.get('id')
        except pymysql.MySQLError as e:
            self.logger.error(str(e))
            raise InternalServerError(str(e))
        finally:
            self.cursor.close()
            self.conn.close()

    def edit_profile(self, user_id:int, 
                         new_full_name:str = None, 
                         new_email:str = None, 
                         new_bio:str = None, 
                         new_linkedin:str = None, 
                         new_tech_stack_names:list = None,
                         new_company:str = None):
        try:
            if new_full_name:
                self.cursor.execute("""UPDATE User SET full_name = %s WHERE id = %s""",(new_full_name, user_id))
            if new_email:
                self.cursor.execute("""UPDATE User SET email = %s WHERE id = %s""",(new_email, user_id))
            if new_tech_stack_names:
                user_tech_stack = self.get_user_tech_stack(user_id)
                tech_stack_vendor_names = [item['name'] for item in user_tech_stack]

                # In with the new
                for tech in new_tech_stack_names - user_tech_stack:
                    self.cursor.execute("SELECT id FROM PublicVendor WHERE vendor_name = %s", (tech,))
                    vendor = self.cursor.fetchone()
                    # If the vendor does not exist, create a new entry in PublicVendor
                    if not vendor:
                        self.cursor.execute("INSERT INTO PublicVendor (vendor_name) VALUES (%s)", (tech,))
                        self.conn.commit()  # Commit the new vendor to the database
                        vendor_id = self.cursor.lastrowid  # Retrieve the ID of the newly inserted vendor
                    else:
                        vendor_id = vendor['id']  # Use the existing ID if the vendor is already in the database

                    # Add the new tech to the user's tech stack
                    self.cursor.execute("""
                        INSERT INTO UserPublicVendor (user_id, vendor_id) 
                        VALUES (%s, %s)
                    """, (user_id, vendor_id))
                    self.conn.commit()  # Commit the new user-tech association to the database

                # Out with the old   
                for tech in tech_stack_vendor_names - new_tech_stack_names:
                    self.cursor.execute("SELECT id FROM PublicVendor WHERE vendor_name = %s", (tech,))
                    vendor = self.cursor.fetchone()
                    self.cursor.execute("DELETE FROM UserPublicVendor WHERE user_id = %s AND vendor_id = %s", (user_id, vendor['id']))
            
            self.cursor.execute("""UPDATE User SET update_time = CURRENT_TIMESTAMP(3) WHERE id = %s""",(user_id))

            if new_bio:
                self.cursor.execute("""UPDATE User SET bio = %s WHERE id = %s""", (new_bio, user_id))
            
            if new_linkedin:
                self.cursor.execute("""UPDATE User SET linkedin_url = %s WHERE id = %s""", (new_linkedin, user_id))
            
            if new_company:
                self.cursor.execute("""UPDATE User SET current_company = %s WHERE id = %s""", (new_company, user_id))
            
            self.cursor.execute("""UPDATE User SET update_time = CURRENT_TIMESTAMP(3) WHERE id = %s""",(user_id))

        except pymysql.MySQLError as e:
            self.conn.rollback()
            self.logger.error(str(e))
            raise InternalServerError(f"Database error: {str(e)}")
        
        finally:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def edit_password(self, user_id:int, old_password:str, new_password:str):
        try:
            # Fetch the current user's password
            self.cursor.execute("SELECT password FROM User WHERE id = %s", (user_id,))
            user_record = self.cursor.fetchone()

            if user_record and check_password_hash(user_record['password'], old_password):
                # If the old password is correct, update with the new hashed password
                hashed_new_password = generate_password_hash(new_password)
                self.cursor.execute("UPDATE User SET password = %s WHERE id = %s", (hashed_new_password, user_id))
                self.conn.commit()
            else:
                raise BadRequest("error: Old Password is Incorrect")
        except pymysql.MySQLError as e:
            self.logger.error(str(e))
            raise InternalServerError(str(e))
        finally:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()        

    def endorse_user(self, user_id:int, endorsee_user_id:int, vendor_id:int):
        try:
            # Insert Endorsement     
            self.cursor.execute(
                """INSERT INTO UserPublicVendorEndorsement (endorser_user_id, endorsee_user_id, vendor_id) VALUES (%s, %s, %s)""",
                (user_id, endorsee_user_id, vendor_id)
            )
        except pymysql.MySQLError as e:
            self.logger.error(str(e))
            self.conn.rollback()
            raise InternalServerError(str(e))
        finally:
            self.conn.commit()
            self.conn.close()
            self.cursor.close()