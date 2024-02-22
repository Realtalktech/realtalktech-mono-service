# models/user.py
from flask import jsonify, make_response
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest, Unauthorized, InternalServerError
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
import pymysql
import re
from utils import DBManager
from auth import Authorizer


class SandUser:
    def __init__(self):
        self.db_manager = DBManager()
        self.conn = self.db_manager.get_db_connection()
        self.cursor = self.conn.cursor()

    def authenticate_returning_user(self, entered_username, entered_password):
        if re.match(r"[^@]+@[^@]+\.[^@]+", entered_username):
            self.cursor.execute("""SELECT username FROM User WHERE email = %s""", (entered_username))
            username = self.cursor.fetchone()
            if not username:
                raise Unauthorized("Invalid Email")
            else:
                entered_username = username['username']
        try:
            user_data = self.fetch_login_credentials_by_username(entered_username)
            if user_data is None:
                raise Unauthorized("Invalid Username")

            if not check_password_hash(entered_password, user_data.get('password')):
                raise Unauthorized("Incorrect Password")
            
            # Authorized, generate token
            user_id = user_data.get('user_id')
            token = Authorizer.generate_token(user_id)
            
            # Grab user details
            user_details = self.get_user_details(user_id, True)
            tech_stack = self.get_user_tech_stack(user_id)
            industry_involvement = self.get_user_industry_involvement(user_id)
            subscribed_discuss_categories = self.get_user_subscribed_discuss_categories(user_id)
            interest_areas = self.get_interest_areas(user_id)

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
            raise InternalServerError(f"Database error: {str(e)}")

        finally:
            self.cursor.close()
            self.conn.close()
    
    def fetch_login_credentials_by_username(self, username):
        # Database lookup to find a user by username
        self.cursor.execute(f"SELECT id, password FROM User WHERE username = %s", (username))
        user_data = self.cursor.fetchone()
        if not user_data:
            return None
        else:
            return {'user_id': user_data.get('id'), 'password': user_data.get('password')}
    
    def get_user_public_profile(self, user_id, requester_id):
        try:
            user_details = self.get_user_details(user_id, False)
            tech_stack = self.get_user_tech_stack(user_id)
            vendors_with_endorsements = self.get_user_techstack_endorsements(user_id, requester_id, tech_stack)
            response = {
                'userDetails': user_details,
                'vendors': vendors_with_endorsements
            }
            return jsonify(response)
        except pymysql.MySQLError as e:
            self.conn.rollback()
            raise InternalServerError(f"Database error: {str(e)}")
        finally:
            self.cursor.close()
            self.conn.close()

    def signup(self, data):
        # Extract data from request
        missing_fields = self.validate_signup_fields(data)
        
        # Raise error if any fields are missing
        if len(missing_fields) > 0:
            missing_fields_str = missing_fields_str = ', '.join(missing_fields)  # Convert the list to a comma-separated string
            error_message = f"Missing required fields: {missing_fields_str}"
            raise BadRequest(error_message)
        
        (full_name, username, email, password, tech_stack, 
        current_company, industry_involvement, subscribed_discuss_categories, 
        interest_areas, linkedin_url, bio) = self.extract_signup_fields(data)

        # Raise error if not in standard email format
        try:
            v = validate_email(email, check_deliverability=True)
            # replace with normalized form
            email = v["email"]
        except EmailNotValidError as e:
            raise BadRequest(str(e))
        
        # Create new user
        try:
            user_id = self.create_user_and_fetch_id(full_name, username, 
                             email, password, current_company, 
                             linkedin_url, bio)
            self.set_subscribed_discuss_categories(user_id, subscribed_discuss_categories)
            self.set_interest_areas(user_id, interest_areas)
            self.set_industry_involvement(user_id, industry_involvement)
            self.set_tech_stack(user_id, tech_stack)

            token = Authorizer.generate_token(user_id)
            response = jsonify(
                    {
                        "message": "Signup successful",
                        "token": token
                    }
                ), 201
            return response

        except pymysql.MySQLError as e:
            self.conn.rollback()
            raise InternalServerError(str(e))
        finally:
            self.cursor.close()
            self.conn.close()

    def validate_signup_fields(self, data):
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

    def extract_signup_fields(self,data):
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
        
        return (full_name, username, email, 
                password, tech_stack, current_company, industry_involvement, 
                categories_of_work, interest_areas, linkedin_url, bio)

    def create_user_and_fetch_id(self, full_name, username, email, password, current_company, linkedin_url, bio):
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
    
    def set_subscribed_discuss_categories(self, user_id, subscribed_discuss_category_names):
        # Link categories of work to User in UserDiscussCategory for feed population
        for work_category in subscribed_discuss_category_names:
            self.cursor.execute("SELECT id FROM DiscussCategory WHERE category_name = %s", (work_category,))
            category_obj = self.cursor.fetchone()
            if category_obj:
                self.cursor.execute("""INSERT INTO UserDiscussCategory (user_id, category_id) VALUES (%s, %s)""",
                            (user_id, category_obj['id']))
    
    def set_interest_areas(self, user_id, interest_area_names):
        # Link interest areas to user
        for area in interest_area_names:
            self.cursor.execute("SELECT id FROM InterestArea WHERE interest_area_name = %s", (area,))
            interest_area_obj = self.cursor.fetchone()
            if interest_area_obj :
                self.cursor.execute("""INSERT INTO UserInterestArea (user_id, interest_area_id) VALUES (%s, %s)""",
                            (user_id, interest_area_obj['id']))     
    
    def set_industry_involvement(self, user_id, industry_involvement_names):
        # Link industry involvement to user
        for industry in industry_involvement_names:
            self.cursor.execute("SELECT id FROM Industry WHERE industry_name = %s", (industry,))
            industry_obj = self.cursor.fetchone()
            if industry_obj:
                self.cursor.execute("""INSERT INTO UserIndustry (user_id, interest_area_id) VALUES (%s, %s)""",
                            (user_id, industry_obj['id']))
    
    def set_tech_stack(self, user_id, tech_stack_vendor_names):
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

    def get_user_tech_stack(self, user_id):
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

    def get_user_industry_involvement(self, user_id):
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

    def get_user_subscribed_discuss_categories(self, user_id):
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

    def get_user_interest_areas(self, user_id):
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

    def get_user_details(self, user_id, is_owner):
        if is_owner:
            self.cursor.execute("""SELECT (id, full_name, username, current_company, email, linkedin_url, bio) FROM User WHERE id = %s""", (user_id))
            userObj = self.cursor.fetchall()
            user_details = {
                'id': userObj.get('id'),
                'fullName': userObj.get('full_name'),
                'username': userObj.get('username'),
                'currentCompany': userObj.get('current_company'),
                'email': userObj.get('email'),
                'linkedinUrl': userObj.get('linkedin_url'),
                'bio': userObj.get('bio')
            }
        else:
            self.cursor.execute("""SELECT (full_name, username, current_company, linkedin_url, bio) FROM User WHERE id = %s""", (user_id))
            userObj = self.cursor.fetchall()
            user_details = {
                'fullName': userObj.get('full_name'),
                'username': userObj.get('username'),
                'currentCompany': userObj.get('current_company'),
                'linkedinUrl': userObj.get('linkedin_url'),
                'bio': userObj.get('bio')
            }

        return user_details          
    
    def convert_user_id_to_username(self, user_id):
        self.cursor.execute("""SELECT username FROM User WHERE id = %s""", user_id)
        user_obj = self.cursor.fetchone()
        return user_obj.get('username')
        
    def convert_username_to_id(self,username):
        self.cursor.execute("""SELECT id FROM User WHERE username = %s""", username)
        user_obj = self.cursor.fetchone()
        return user_obj.get('id')

    def get_user_techstack_endorsements(self, user_id, requester_id, tech_stack):
        # Process associated vendors from tech_stack and check endorsements
        vendors_with_endorsements = []
        for item in tech_stack:
            endorsement = self.check_endorsement_from_id(item['id'], user_id, requester_id)
            vendors_with_endorsements.append({
                'vendorId': item['id'],
                'vendorName': item['name'],
                'endorsedByRequester': endorsement
            })
        return vendors_with_endorsements

    def check_endorsement_from_id(self, vendor_id, user_id, requester_id):
        # Check for endorsement
        self.cursor.execute("""
            SELECT COUNT(*) AS endorsement_count
            FROM UserPublicVendorEndorsement
            WHERE endorser_user_id = %s AND endorsee_user_id = %s AND vendor_id = %s
        """, (requester_id, user_id, vendor_id))
        endorsement = self.cursor.fetchone().get('endorsement_count') > 0
        return endorsement

    @classmethod 
    def find_by_id(cls, cursor, user_id,
                   subscribed_categories = False,
                   tech_stack = False,
                   interest_areas = False,
                   industry_involvement = False,
                   needed_info = []
                   ):
        # Database lookup to find username
        cursor.execute("SELECT username FROM User WHERE id = %s", (user_id))
        username = cursor.fetchone()
        if not username:
            return None
        else:
            username = username['username']
            return cls.find_by_username(cursor, username, needed_info, subscribed_categories,
                                        tech_stack, interest_areas, industry_involvement)

    @classmethod
    def find_by_username(cls, cursor, username,
                         needed_info = [],
                         subscribed_categories = False,
                         tech_stack = False,
                         interest_areas = False,
                         industry_involvement = False
                        ):
        
        fields_str = ','.join(needed_info)

        # Database lookup to find a user by username
        cursor.execute(f"SELECT {fields_str} FROM User WHERE username = %s", (username))
        user_data = cursor.fetchone()
        
        if user_data:
            # Create User instance with only the available info
            user = cls(
                id=user_data.get('id'),
                full_name = user_data.get('full_name'),
                current_company = user_data.get('current_company'),
                email = user_data.get('email'),
                linkedin_url = user_data.get('linkedin_url'),
                bio = user_data.get('bio'),
                username = username,
                password=user_data.get('password')
            )
            if subscribed_categories:
                user.subscribed_discuss_category_names, user.subscribed_discuss_category_ids = cls.get_subscribed_discuss_categories(cursor, user.id)

            if tech_stack:
                user.tech_stack_vendor_names, user.tech_stack_vendor_ids = user.get_tech_stack(cursor, user.id)

            if interest_areas:
                user.interest_area_names, user.interest_area_ids = user.get_interest_areas(cursor, user.id)

            if industry_involvement:
                user.industry_involvement_names, user.industry_involvement_ids = user.get_industry_involvement(cursor, user.id)
            
            return user
        
        else:
            return None

    def get_subscribed_discuss_categories(self, cursor, user_id):
         # Database lookup to find subscribed discuss categories (categories of work)
        cursor.execute(
            """SELECT category_id FROM UserDiscussCategory WHERE user_id = %s""",
            (user_id)
        )

        discuss_categories = cursor.fetchall()
        subscribed_discuss_category_names = []
        subscribed_discuss_category_ids = []
        for category in discuss_categories:
            cursor.execute(
                """SELECT category_name FROM DiscussCategory WHERE id = %s""",
                (category['category_id'])
            )
            category_name = cursor.fetchone()['category_name']
            subscribed_discuss_category_names.append(category_name)
            subscribed_discuss_category_ids.append(category['category_id'])

        return subscribed_discuss_category_names, subscribed_discuss_category_ids  

    def get_tech_stack(self, cursor, user_id):
        # Database lookup to find tech_stack (UserPublicVendor)
        cursor.execute(
            """SELECT vendor_id FROM UserPublicVendor WHERE user_id = %s""",
            (user_id)
        )
        user_skills = cursor.fetchall()
        tech_stack_vendor_names = []
        tech_stack_vendor_ids = []

        for skill in user_skills:
            cursor.execute(
                """SELECT vendor_name FROM PublicVendor WHERE id = %s""",
                (skill['vendor_id'])
            )
            tech_stack_vendor_name = cursor.fetchone()['vendor_name']
            tech_stack_vendor_names.append(tech_stack_vendor_name)
            tech_stack_vendor_ids.append(skill['vendor_id'])
        
        return tech_stack_vendor_names, tech_stack_vendor_ids
    
    def get_interest_areas(self, cursor, user_id):
        # Database lookup to find interest area names and ids
        cursor.execute(
            """SELECT interest_area_id FROM UserInterestArea WHERE user_id = %s""",
            (user_id)
        )
        interest_area_objs = cursor.fetchall()
        interest_area_names = []
        interest_area_ids = []

        for area in interest_area_objs:
            cursor.execute(
                """SELECT interest_area_name FROM InterestArea WHERE id = %s""",
                (area['interest_area_id'])
            )
            interest_area_name = cursor.fetchone()['interest_area_name']
            interest_area_names.append(interest_area_name)
            interest_area_ids.append(area['interest_area_id'])
        
        return interest_area_names, interest_area_ids

    def get_industry_involvement(self, cursor, user_id):
        # Database lookup to find industry involvement
        cursor.execute(
            """SELECT industry_id FROM UserIndustry WHERE user_id = %s""",
            (user_id)
        )
        user_industries = cursor.fetchall()
        industry_involement_names = []
        industry_involvement_ids = []

        for industry in user_industries:
            cursor.execute(
                """SELECT industry_name FROM Industry WHERE id = %s""",
                (industry['industry_id'])
            )
            industry_name = cursor.fetchone()['industry_name']
            industry_involement_names.append(industry_name)
            industry_involvement_ids.append(industry['industry_id'])
        
        return industry_involement_names, industry_involvement_ids

    def receive_endorsement(self, vendor_id, endorser_id, cursor):
        cursor.execute(
            """INSERT INTO UserPublicVendorEndorsement (endorser_user_id, endorsee_user_id, vendor_id) VALUES (%s, %s, %s)""",
            (endorser_id, self.id, vendor_id)
        )        
        
    def fetch_account_creation_time(self, cursor):
        cursor.execute("""SELECT creation_time FROM User WHERE id=%s""",(self.id))
        creation_time = cursor.fetchone()['creation_time']
        creation_time = creation_time.isoformat()
        return creation_time
    
    def fetch_account_update_time(self, cursor):
        cursor.execute("""SELECT update_time FROM User WHERE id=%s""",(self.id))
        update_time = cursor.fetchone()['update_time']
        update_time = update_time.isoformat()
        return update_time
    
    def edit_profile(self, cursor,
                     new_full_name = None,
                     new_email = None,
                     new_tech_stack = None
                    ):
        
        if new_full_name:
            cursor.execute("""UPDATE User SET full_name = COALESCE(%s, full_name)""",(new_full_name))
        if new_email:
            cursor.execute("""UPDATE User SET email = %s""",(new_email))
        if new_tech_stack:
            self.get_tech_stack(cursor, self.id)

            # In with the new
            for tech in new_tech_stack - self.tech_stack_vendor_names:
                cursor.execute("SELECT id FROM PublicVendor WHERE vendor_name = %s", (tech,))
                vendor = cursor.fetchone()
                if vendor:
                    cursor.execute("""
                        INSERT INTO UserPublicVendor (user_id, vendor_id) 
                        VALUES (%s, %s)
                    """, (self.id, vendor['id']))
            
            # Out with the old
            for tech in self.tech_stack_vendor_names - new_tech_stack:
                self.tech_stack_vendor_ids[
                    self.tech_stack_vendor_names.index(tech)
                ]
        
        cursor.execute("""UPDATE User SET update_time = CURRENT_TIMESTAMP(3) WHERE id = %s""",(self.id))

