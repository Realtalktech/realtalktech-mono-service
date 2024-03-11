# models/user.py
from flask import jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pymysql
import re

class User:
    def __init__(
        self,
        id=None,
        full_name=None,
        username=None,
        email=None,
        password=None,
        linkedin_url=None,
        bio = None,
        tech_stack_vendor_names=[], # Tech Stack
        tech_stack_vendor_ids=[],
        current_company=None,
        industry_involvement_names=[], # What industry are you in?
        industry_involvement_ids = [],
        subscribed_discuss_category_names =[], # What do you do?
        subscribed_discuss_category_ids = [],
        interest_area_names=[], # Interest areas
        interest_area_ids=[]
    ):
        self.id = id
        self.full_name = full_name
        self.username = username
        self.email = email
        self.password = password
        self.linkedin_url = linkedin_url
        self.bio = bio
        self.tech_stack_vendor_names = tech_stack_vendor_names
        self.tech_stack_vendor_ids = tech_stack_vendor_ids
        self.current_company = current_company
        self.industry_involvement_names = industry_involvement_names
        self.industry_involvement_ids = industry_involvement_ids
        self.subscribed_discuss_category_names = subscribed_discuss_category_names
        self.subscribed_discuss_category_ids = subscribed_discuss_category_ids
        self.interest_area_names = interest_area_names
        self.interest_area_ids = interest_area_ids
    
    def create_user(self,cursor):
        # Hash the password
        hashed_password = generate_password_hash(self.password)

        values_to_insert = (
            self.full_name or '',  # Replaces None with empty string
            self.username,  # NOT NULL in DB schema
            self.current_company,  # NOT NULL in DB schema
            self.email,  # NOT NULL in DB schema
            self.linkedin_url or '',  # Replaces None with empty string
            self.bio or '',  # Replaces None with empty string
            hashed_password  # NOT NULL in DB schema
        )

        # Insert user into database
        cursor.execute("""
            INSERT INTO User (full_name, username, current_company, email, linkedin_url, bio, password) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, values_to_insert)
        user_id = cursor.lastrowid # Get ID of newly inserted user
        self.id = user_id
        self.set_subscribed_discuss_categories(cursor)
        self.set_interest_areas(cursor)
        self.set_industry_involvement(cursor)
        self.set_tech_stack(cursor)

    @classmethod
    def authenticate_and_create_returning_user(cls, cursor, entered_username, entered_password):

        if re.match(r"[^@]+@[^@]+\.[^@]+", entered_username):
            cursor.execute("""SELECT username FROM User WHERE email = %s""", (entered_username))
            username = cursor.fetchone()
            if not username:
                return None
            else:
                entered_username = username['username']

        # Fetch the user by username
        user = cls.find_by_username(cursor, 
                                    username = entered_username,
                                    needed_info=['id', 'full_name', 'password', 'current_company', 'email', 'linkedin_url', 'bio'],
                                    tech_stack=True,
                                    interest_areas=True,
                                    industry_involvement=True,
                                    subscribed_categories=True
                                    )
        if user and check_password_hash(user.password, entered_password):
            # Authentication successful
            return user
        else:
            return None
    
    def set_subscribed_discuss_categories(self, cursor):
        # Link categories of work to User in UserDiscussCategory for feed population
        for work_category in self.subscribed_discuss_category_names:
            cursor.execute("SELECT id FROM DiscussCategory WHERE category_name = %s", (work_category,))
            category_obj = cursor.fetchone()
            if category_obj:
                cursor.execute("""INSERT INTO UserDiscussCategory (user_id, category_id) VALUES (%s, %s)""",
                            (self.id, category_obj['id']))
    
    def set_interest_areas(self, cursor):
        # Link interest areas to user
        for area in self.interest_area_names:
            cursor.execute("SELECT id FROM InterestArea WHERE interest_area_name = %s", (area,))
            interest_area_obj = cursor.fetchone()
            if interest_area_obj :
                cursor.execute("""INSERT INTO UserInterestArea (user_id, interest_area_id) VALUES (%s, %s)""",
                            (self.id, interest_area_obj['id']))     
    
    def set_industry_involvement(self, cursor):
        # Link industry involvement to user
        for industry in self.industry_involvement_names:
            cursor.execute("SELECT id FROM Industry WHERE industry_name = %s", (industry,))
            industry_obj = cursor.fetchone()
            if industry_obj:
                cursor.execute("""INSERT INTO UserIndustry (user_id, industry_id) VALUES (%s, %s)""",
                            (self.id, industry_obj['id']))
    
    def set_tech_stack(self, cursor):
        # Link tech stack to user
        for tech in self.tech_stack_vendor_names:
            cursor.execute("SELECT id FROM PublicVendor WHERE vendor_name = %s", (tech,))
            vendor = cursor.fetchone()
            if vendor:
                cursor.execute("""
                    INSERT INTO UserPublicVendor (user_id, vendor_id) 
                    VALUES (%s, %s)
                """, (self.id, vendor['id']))
            else:
                cursor.execute("""
                    INSERT INTO PublicVendor (vendor_name) VALUES (%s)
                """, (tech))

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
        cursor.execute(f"SELECT {fields_str} FROM User WHERE username = %s", (username))
        return cls.find_by(cursor, subscribed_categories, tech_stack, interest_areas, industry_involvement)
    
    @classmethod
    def find_by_email(cls, cursor, email,
            needed_info = [],
            subscribed_categories = False,
            tech_stack = False,
            interest_areas = False,
            industry_involvement = False
        ):
        fields_str = ','.join(needed_info)
        cursor.execute(f"SELECT {fields_str} FROM User WHERE email = %s", (email))
        return cls.find_by(cursor, subscribed_categories, tech_stack, interest_areas, industry_involvement)

    @classmethod
    def find_by(cls, cursor,
            subscribed_categories = False,
            tech_stack = False,
            interest_areas = False,
            industry_involvement = False
        ):
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
                username = user_data.get('username'),
                password=user_data.get('password')
            )
            if subscribed_categories:
                user.subscribed_discuss_category_names, user.subscribed_discuss_category_ids = user.get_subscribed_discuss_categories(cursor, user.id)

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

    @classmethod
    def check_endorsement_from_id(cls, vendor_id, user_id, endorsee_id, cursor):
        # Check for endorsement
        cursor.execute("""
            SELECT COUNT(*) AS endorsement_count
            FROM UserPublicVendorEndorsement
            WHERE endorser_user_id = %s AND vendor_id = %s AND endorsee_user_id = %s
        """, (user_id, vendor_id, endorsee_id))
        endorsement = cursor.fetchone()['endorsement_count'] > 0
        return endorsement
    
    @classmethod
    def get_endorsements_count(cls, vendor_id, endorsee_id, cursor):
        print("ENDORSEGETW", vendor_id, endorsee_id)
        # Check for endorsement
        cursor.execute("""
            SELECT COUNT(*) AS endorsement_count
            FROM UserPublicVendorEndorsement
            WHERE vendor_id = %s AND endorsee_user_id = %s
        """, (vendor_id, endorsee_id))
        endorsementCount = cursor.fetchone()['endorsement_count']
        return endorsementCount

    def receive_endorsement(self, vendor_id, endorser_id, cursor):
        print("ENDORSEINSERTW", vendor_id, endorser_id)
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
                     new_tech_stack = None,
                     new_bio = None,
                     new_linkedin = None,
                     new_company = None,
                     new_username = None,
                    ):
        
        if new_full_name:
            cursor.execute("""UPDATE User SET full_name = %s WHERE id = %s""",(new_full_name, self.id))
        if new_email:
            cursor.execute("""UPDATE User SET email = %s WHERE id = %s""",(new_email, self.id))
        if new_tech_stack:
            self.get_tech_stack(cursor, self.id)

            # In with the new
            # techAdd = set()
            # # for tech in new_tech_stack:
            # #     techAdd.add(tech)
            # # for tech in self.tech_stack_vendor_names:
            # #     techAdd.add(tech)
            # techAdd.update(new_tech_stack)
            # techAdd.update(self.tech_stack_vendor_names)
            # for tech in new_tech_stack - self.tech_stack_vendor_names:
            for tech in list(set(new_tech_stack) - set(self.tech_stack_vendor_names)):
                # self.cursor.execute("SELECT id FROM PublicVendor WHERE vendor_name = %s", (tech,))
                cursor.execute("SELECT id FROM PublicVendor WHERE vendor_name = %s", (tech,))
                vendor = cursor.fetchone()

                # If the vendor does not exist, create a new entry in PublicVendor
                if not vendor:
                    cursor.execute("INSERT INTO PublicVendor (vendor_name) VALUES (%s)", (tech,))
                    # self.conn.commit()  # Commit the new vendor to the database
                    vendor_id = cursor.lastrowid  # Retrieve the ID of the newly inserted vendor
                else:
                    vendor_id = vendor['id']  # Use the existing ID if the vendor is already in the database

                # Add the new tech to the user's tech stack
                cursor.execute("""
                    INSERT INTO UserPublicVendor (user_id, vendor_id) 
                    VALUES (%s, %s)
                """, (self.id, vendor_id))
                # self.conn.commit()  # Commit the new user-tech association to the database

            # Out with the old   
            # for tech in self.tech_stack_vendor_names - new_tech_stack:
            for tech in list(set(self.tech_stack_vendor_names) - set(new_tech_stack)):
                vendor_id = self.tech_stack_vendor_ids[self.tech_stack_vendor_names.index(tech)]
                cursor.execute("DELETE FROM UserPublicVendor WHERE user_id = %s AND vendor_id = %s", (self.id, vendor_id))

        if new_bio:
            cursor.execute("""UPDATE User SET bio = %s WHERE id = %s""", (new_bio, self.id))
        
        if new_linkedin:
            cursor.execute("""UPDATE User SET linkedin_url = %s WHERE id = %s""", (new_linkedin, self.id))
        
        if new_company:
            cursor.execute("""UPDATE User SET current_company = %s WHERE id = %s""", (new_company, self.id))

        if new_username:
            cursor.execute("""UPDATE User SET username = %s WHERE id = %s""", (new_username, self.id))
        
        cursor.execute("""UPDATE User SET update_time = CURRENT_TIMESTAMP(3) WHERE id = %s""",(self.id))

