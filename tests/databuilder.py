import sqlite3
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from typing import Dict
from rtt_data_app.models.user import User
from rtt_data_app.models import PublicVendor, UserPublicVendor, UserPublicVendorEndorsement, UserDiscussCategory, DiscussCategory, PostUpvote
from rtt_data_app.models import DiscoverVendor, Post, Comment, CommentUpvote
from sqlalchemy import func

class DataBuilder:
    def __init__():
        pass

    def init_test_database():
        # Connect to test database, specify the path to SQLite test database file

        # SQLite does not:
            # Enforce the length of VARCHAR 
            # Support DATETIME(3)
            # Support AUTO_INCREMENT
        # SQLite 'INTEGER PRIMARY KEY' auto-increments

        # Recreate the tables for the test database
        # Note: Removed AUTO_INCREMENT, changed DATETIME(3) to DATETIME

        connection = sqlite3.connect('tests/sqlite/test_database.db')
        cursor = connection.cursor()
        cursor.executescript('''
            DROP TABLE IF EXISTS UserIndustry;
            DROP TABLE IF EXISTS UserInterestArea;
            DROP TABLE IF EXISTS UserDiscussCategory;
            DROP TABLE IF EXISTS PostDiscussCategory;
            DROP TABLE IF EXISTS VendorDiscoverCategory;
            DROP TABLE IF EXISTS UserPublicVendor;
            DROP TABLE IF EXISTS PostDiscoverVendor;
            DROP TABLE IF EXISTS UserPublicVendorEndorsement;
            DROP TABLE IF EXISTS PublicVendor;
            DROP TABLE IF EXISTS DiscoverVendor;
            DROP TABLE IF EXISTS PostUpvote;
            DROP TABLE IF EXISTS CommentUpvote;
            DROP TABLE IF EXISTS CommentTag;
            DROP TABLE IF EXISTS Comment;
            DROP TABLE IF EXISTS Post;
            DROP TABLE IF EXISTS UserIndustry;
            DROP TABLE IF EXISTS InterestArea;
            DROP TABLE IF EXISTS Industry;
            DROP TABLE IF EXISTS DiscoverCategory;
            DROP TABLE IF EXISTS DiscussCategory;
            DROP TABLE IF EXISTS User;

            CREATE TABLE User (
                id INTEGER PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                username VARCHAR(255) UNIQUE NOT NULL,
                current_company VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                linkedin_url VARCHAR(255),
                bio VARCHAR(255),
                password VARCHAR(255) NOT NULL,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            );
                             
            CREATE TABLE Post (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                is_anonymous BOOLEAN NOT NULL,
                title VARCHAR(255) NOT NULL,
                body TEXT NOT NULL,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES User(id)
            );
                             
            CREATE TABLE DiscussCategory (
                id INTEGER PRIMARY KEY,
                category_name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            );
                             
            CREATE TABLE DiscoverCategory (
                id INTEGER PRIMARY KEY,
                category_name VARCHAR(255) UNIQUE NOT NULL,
                icon TEXT NOT NULL,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            );
                             
            CREATE TABLE InterestArea (
                id INTEGER PRIMARY KEY,
                interest_area_name VARCHAR(255) UNIQUE NOT NULL,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            );
                             
            CREATE TABLE Industry (
                id INTEGER PRIMARY KEY,
                industry_name VARCHAR(255) UNIQUE NOT NULL,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP    
            );
                             
            CREATE TABLE UserIndustry (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                industry_id INTEGER,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES User(id),
                FOREIGN KEY (industry_id) REFERENCES Industry(id)    
            );
                             
            CREATE TABLE UserInterestArea (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                interest_area_id INTEGER,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES User(id),
                FOREIGN KEY (interest_area_id) REFERENCES InterestArea(id)
            );
                             
            CREATE TABLE UserDiscussCategory (
                user_id INTEGER,
                category_id INTEGER,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES User(id),
                FOREIGN KEY (category_id) REFERENCES DiscussCategory(id),
                PRIMARY KEY (user_id, category_id)
            );
                             
            CREATE TABLE PostDiscussCategory (
                post_id INTEGER,
                category_id INTEGER,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES Post(id),
                FOREIGN KEY (category_id) REFERENCES DiscussCategory(id),
                PRIMARY KEY (post_id, category_id)
            );
                             
            CREATE TABLE DiscoverVendor (
                id INTEGER PRIMARY KEY,
                vendor_name VARCHAR(255) UNIQUE NOT NULL,
                vendor_type VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                vendor_hq VARCHAR(255),
                total_employees INTEGER,
                vendor_homepage_url VARCHAR(255),
                vendor_logo_url VARCHAR(255),
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            );
                             
            CREATE TABLE PublicVendor (
                id INTEGER PRIMARY KEY,
                discover_vendor_id INTEGER,  -- Nullable foreign key referencing DiscoverVendor
                vendor_name VARCHAR(255) UNIQUE NOT NULL,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (discover_vendor_id) REFERENCES DiscoverVendor(id)  -- Foreign key constraint
            );
                             
            CREATE TABLE UserPublicVendorEndorsement (
                id INTEGER PRIMARY KEY,
                endorser_user_id INTEGER,
                endorsee_user_id INTEGER,
                vendor_id INTEGER,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vendor_id) REFERENCES PublicVendor(id),
                FOREIGN KEY (endorser_user_id) REFERENCES User(id),
                FOREIGN KEY (endorsee_user_id) REFERENCES User(id)
            );
                             
            CREATE TABLE VendorDiscoverCategory (
                vendor_id INTEGER,
                category_id INTEGER,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vendor_id) REFERENCES DiscoverVendor(id),
                FOREIGN KEY (category_id) REFERENCES DiscoverCategory(id),
                PRIMARY KEY (vendor_id, category_id)
            );
                             
            CREATE TABLE UserPublicVendor (
                user_id INTEGER,
                vendor_id INTEGER,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES User(id),
                FOREIGN KEY (vendor_id) REFERENCES PublicVendor(id),
                PRIMARY KEY (user_id, vendor_id)
            );
                             
            CREATE TABLE PostDiscoverVendor (
                post_id INTEGER,
                vendor_id INTEGER,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES Post(id),
                FOREIGN KEY (vendor_id) REFERENCES DiscoverVendor(id),
                PRIMARY KEY (post_id, vendor_id)
            );
                             
            CREATE TABLE Comment (
                id INTEGER PRIMARY KEY,
                post_id INTEGER,
                user_id INTEGER,
                comment_text TEXT NOT NULL,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES Post(id),
                FOREIGN KEY (user_id) REFERENCES User(id)
            );
                             
            CREATE TABLE CommentTag (
                id INTEGER PRIMARY KEY,
                comment_id INTEGER,
                tagged_user_id INTEGER,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (comment_id) REFERENCES Comment(id),
                FOREIGN KEY (tagged_user_id) REFERENCES User(id)
            );
                             
            CREATE TABLE PostUpvote (
                id INTEGER PRIMARY KEY,
                post_id INTEGER,
                user_id INTEGER,
                is_downvote BOOLEAN NOT NULL,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES Post(id),
                FOREIGN KEY (user_id) REFERENCES User(id)
            );
                             
            CREATE TABLE CommentUpvote (
                id INTEGER PRIMARY KEY,
                comment_id INTEGER,
                user_id INTEGER,
                is_downvote BOOLEAN NOT NULL,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (comment_id) REFERENCES Comment(id),
                FOREIGN KEY (user_id) REFERENCES User(id)
            );
                             
            PRAGMA foreign_keys = ON;
        ''')

        # Commit changes and close the connection
        connection.commit()
        connection.close()

class DataInserter:
    def __init__(self):
        pass

    def init_test_database(self):
        """Inserts discuss categories, industries, interest_areas, discover_categories """
        # Establish database connection and call methods to insert data
        conn = sqlite3.connect('tests/sqlite/test_database.db')
        self.cursor = conn.cursor()
        self.test_user_ids = []
        self.discuss_categories = ["AI", "Engineering", "Operations", "Marketing"]
        self.industries = ["AdTech", "Angel or VC Firm", "AI", "Automation"]
        self.interest_areas = ["Sales Tools", "Marketing", "Analytics Tools & Software"]
        self.discover_categories = ["Sales Tools", "Marketing","Collaboration & Productivity", "Commerce"]

        self.vendors = ["Salesforce", "Snowflake", "Databricks", "Datadog"]
        try:
            self.insert_discuss_categories()
            self.insert_discover_categories()
            self.insert_interest_areas()
            self.insert_industries()
            self.insert_vendors()

        finally:
            conn.commit()
            self.cursor.close()
            conn.close()
    
    def init_sample_posts(self):
        conn = sqlite3.connect('tests/sqlite/test_database.db')
        self.cursor = conn.cursor()
        self.test_user_ids = []
        self.discuss_categories = ["AI", "Engineering", "Operations", "Marketing"]
        self.industries = ["AdTech", "Angel or VC Firm", "AI", "Automation"]
        self.interest_areas = ["Sales Tools", "Marketing", "Analytics Tools & Software"]
        self.discover_categories = ["Sales Tools", "Marketing","Collaboration & Productivity", "Commerce"]

        self.vendors = ["Salesforce", "Snowflake", "Databricks", "Datadog"]
        try:
            self.insert_test_users()
            self.insert_post_1()
            self.insert_post_2()
            self.insert_post_3()
            self.insert_post_4()
        except Exception as e:
            print(str(e))

        finally:
            conn.commit()
            self.cursor.close()
            conn.close()
    
    def insert_discover_categories(self):
        # Insert Categories
        for category in self.discover_categories:
                icon = ""
                self.cursor.execute("INSERT INTO DiscoverCategory (category_name, icon) VALUES (?,?)", (category,icon))

    def insert_discuss_categories(self):
        """Insert discuss categories into the DiscussCategory table"""
        for category in self.discuss_categories:
            self.cursor.execute(
                """INSERT INTO DiscussCategory (category_name) VALUES (?)""",
                (category,)
            )

    def insert_interest_areas(self):
        """Insert interest areas into the InterestArea table"""
        for area in self.interest_areas:
            self.cursor.execute(
                """INSERT INTO InterestArea (interest_area_name) VALUES (?)""",
                (area,)
            )

    def insert_industries(self):
        """Insert industries into the Industry table"""
        for industry in self.industries:
            self.cursor.execute(
                """INSERT INTO Industry (industry_name) VALUES (?)""",
                (industry,)
            )
    
    def insert_vendors(self):
        """Insert vendors into DiscoverVendor and PublicVendor tables, under category "Sales" (id = 1)"""
        for vendor in self.vendors:
            self.cursor.execute(
                """INSERT INTO DiscoverVendor (vendor_name, vendor_type, description)
                VALUES(?, ?, ?)""", (vendor, vendor, vendor)
            )
            vendor_id = self.cursor.lastrowid
            self.cursor.execute(
                """INSERT INTO VendorDiscoverCategory(vendor_id, category_id) VALUES(?,?)""",(vendor_id,1)
            )
            self.cursor.execute(
                """INSERT INTO PublicVendor (vendor_name)
                VALUES(?)""", (vendor,)
            )

    def insert_test_users(self):
        """Inserts four test users"""
        names = ["Elon Gates", "Bill Musk", "Mary Barra", "Kamala Clinton"]
        employers = ["SuperchargedSoftware", "MacroAdvanced", "General Autos", "Capitol Tech"]
        for i, name in enumerate(names):
            username = name.replace(" ", "").lower()
            email = f"{username}@example.com"
            password = generate_password_hash('password')
            current_company = employers[i]
            
            quarter_size = len(self.discuss_categories) // len(names)
            user_discuss_categories = self.discuss_categories[i * quarter_size: (i + 1) * quarter_size]
            
            quarter_size = len(self.industries) // len(names)
            user_industries = self.industries[i * quarter_size: (i + 1) * quarter_size]
            
            quarter_size = len(self.interest_areas) // len(names)
            user_interest_areas = self.interest_areas[i * quarter_size: (i + 1) * quarter_size]

            self.cursor.execute(
                """INSERT INTO User (full_name, username, password, current_company, email) 
                VALUES (?, ?, ?, ?, ?)""", (name, username, password, current_company, email)
            )

            self.cursor.execute("SELECT last_insert_rowid()")
            user_id = self.cursor.fetchone()[0]
            self.test_user_ids.append(user_id)

            # Subscribe user to categories
            for category in user_discuss_categories:
                self.cursor.execute("""SELECT id FROM DiscussCategory WHERE category_name = ?""", (category,))
                category_id = self.cursor.fetchone()
                if category_id:
                    self.cursor.execute("""INSERT INTO UserDiscussCategory (user_id, category_id) VALUES (?, ?)""", (user_id, category_id[0]))
                else:
                    print("Could not find category named:", category)
            
            # Subscribe user to industries
            for industry in user_industries:
                self.cursor.execute("""SELECT id FROM Industry WHERE industry_name = ?""", (industry,))
                industry_id = self.cursor.fetchone()
                if industry_id:
                    self.cursor.execute("""INSERT INTO UserIndustry (user_id, industry_id) VALUES (?, ?)""", (user_id, industry_id[0]))
                else:
                    print("Could not find industry named:", industry)

            # Subscribe user to interest area
            for area in user_interest_areas:
                self.cursor.execute("""SELECT id FROM InterestArea WHERE interest_area_name = ?""", (area,))
                area_id = self.cursor.fetchone()
                if area_id:
                    self.cursor.execute("""INSERT INTO UserInterestArea (user_id, interest_area_id) VALUES (?, ?)""", (user_id, area_id[0]))
                else:
                    print("Could not find interest_area named:", area)

    def insert_post_1(self):
        """Inserts a post from Elon Gates, tags Salesforce, links category as engineering comments from Bill and Mary, Elon likes Bill's comment"""
        # Insert post
        self.cursor.execute(
            """INSERT INTO Post (user_id, is_anonymous, title, body) VALUES (?, ?, ?, ?)""",
            (self.test_user_ids[0], 0, "Salesforce is awesome", "I've sold so many cars.")
        )
        self.cursor.execute("SELECT last_insert_rowid()")
        post_id = self.cursor.fetchone()[0]

        # Tag Salesforce in post
        self.cursor.execute(
            """INSERT INTO PostDiscoverVendor (post_id, vendor_id) VALUES (?,?)""",
            (post_id, 2)
        )
        # Insert comment from Bill
        self.cursor.execute(
            """INSERT INTO Comment (post_id, user_id, comment_text) VALUES (?, ?, ?)""",
            (post_id, self.test_user_ids[1], "Salesforce is a great tool!")
        )
        self.cursor.execute("SELECT last_insert_rowid()")
        comment_id = self.cursor.fetchone()[0]

        # Insert comment from Mary
        self.cursor.execute(
            """INSERT INTO Comment (post_id, user_id, comment_text) VALUES (?, ?, ?)""",
            (post_id, self.test_user_ids[2], "Maybe I should try it so I can sell more cars too")
        )

        # Elon likes Bill's comment
        self.cursor.execute(
            """INSERT INTO CommentUpvote (comment_id, is_downvote, user_id) VALUES (?, ?, ?)""",
            (comment_id, 0, self.test_user_ids[0])
        )

        # Link to engineering
        self.link_category_with_post(post_id, 2)

    def insert_post_2(self):
        """Inserts a post from Elon Gates about HubSpot, links category as engineering, with comments and likes"""
        # Insert post about HubSpot
        self.cursor.execute(
            """INSERT INTO Post (user_id, is_anonymous, title, body) VALUES (?, ?, ?, ?)""",
            (self.test_user_ids[0], 0, "HubSpot Revolution", "HubSpot has changed the way we market!")
        )
        self.cursor.execute("SELECT last_insert_rowid()")
        post_id = self.cursor.fetchone()[0]

        # Tag HubSpot in post
        self.cursor.execute(
            """INSERT INTO PostDiscoverVendor (post_id, vendor_id) VALUES (?, ?)""",
            (post_id, 5)
        )

        # Comments and likes
        self.insert_comment_and_like(post_id, self.test_user_ids[2], "HubSpot is indeed a game-changer!", self.test_user_ids[1])

        # Link to engineering
        self.link_category_with_post(post_id, 2)

    def insert_post_3(self):
        """Inserts an anonymous post by Elon Gates, links category as engineering, no tags, with comments"""
        # Insert anonymous post
        self.cursor.execute(
            """INSERT INTO Post (user_id, is_anonymous, title, body) VALUES (?, ?, ?, ?)""",
            (self.test_user_ids[0], 1, "Anonymous Insights", "What are your thoughts on the future of AI in sales?")
        )
        self.cursor.execute("SELECT last_insert_rowid()")
        post_id = self.cursor.fetchone()[0]

        # Comments
        self.insert_comment(post_id, self.test_user_ids[1], "AI is going to be crucial in understanding customer needs.")

        # Link to engineering
        self.link_category_with_post(post_id, 2)

    def insert_post_4(self):
        """Inserts a post from Elon Gates about Zendesk Sell,  links category as engineering, with comments and likes"""
        # Insert post about Zendesk Sell
        self.cursor.execute(
            """INSERT INTO Post (user_id, is_anonymous, title, body) VALUES (?, ?, ?, ?)""",
            (self.test_user_ids[0], 0, "Zendesk Sell's Impact", "Our sales team loves Zendesk Sell!")
        )
        self.cursor.execute("SELECT last_insert_rowid()")
        post_id = self.cursor.fetchone()[0]

        # Tag Zendesk Sell in post
        self.cursor.execute(
            """INSERT INTO PostDiscoverVendor (post_id, vendor_id) VALUES (?, ?)""",
            (post_id, 42)
        )

        # Comments and likes
        self.insert_comment_and_like(post_id, self.test_user_ids[3], "It's a superb tool!", self.test_user_ids[0])

        # Link to engineering
        self.link_category_with_post(post_id, 2)

    def insert_post_5(self):
        """Inserts a post from Bill Musk about Zendesk Sell, links category as engineering, with comments and likes"""
        # Insert post about Zendesk Sell
        self.cursor.execute(
            """INSERT INTO Post (user_id, is_anonymous, title, body) VALUES (?, ?, ?, ?)""",
            (self.test_user_ids[1], 0, "Zendesk Sell's Impact", "Our sales team loves Zendesk Sell!")
        )
        self.cursor.execute("SELECT last_insert_rowid()")
        post_id = self.cursor.fetchone()[0]

        # Tag Zendesk Sell in post
        self.cursor.execute(
            """INSERT INTO PostDiscoverVendor (post_id, vendor_id) VALUES (?, ?)""",
            (post_id, 42)
        )

        # Comments and likes
        self.insert_comment_and_like(post_id, self.test_user_ids[3], "It's a superb tool!", self.test_user_ids[0])

        # Link to engineering
        self.link_category_with_post(post_id, 2)

    def insert_comment(self, post_id, user_id, text):
        """Helper function to insert a comment"""
        self.cursor.execute(
            """INSERT INTO Comment (post_id, user_id, comment_text) VALUES (?, ?, ?)""",
            (post_id, user_id, text)
        )

    def insert_comment_and_like(self, post_id, commenter_id, comment_text, liker_id):
        """Helper function to insert a comment and a like"""
        self.insert_comment(post_id, commenter_id, comment_text)
        self.cursor.execute("SELECT last_insert_rowid()")
        comment_id = self.cursor.fetchone()[0]

        # Insert like
        self.cursor.execute(
            """INSERT INTO CommentUpvote (comment_id, is_downvote, user_id) VALUES (?, ?, ?)""",
            (comment_id, 0, liker_id)
        )
    
    def link_category_with_post(self, post_id, category_id):
        self.cursor.execute("""INSERT INTO PostDiscussCategory (post_id, category_id) VALUES (?, ?)""", (post_id, category_id))


class UserFactory:

    def get_id_stub(user:User) -> int:
        id_stub = user.username[-1]
        return id_stub

    def get_login_response(user:User) -> Dict:
        return{
                "message":"Login successful",
                "token":{"MockToken":"MockToken"},
                'userDetails': {
                    'bio': user.bio,
                    'currentCompany': user.current_company,
                    'email': user.email,
                    'fullname': user.full_name,
                    'username': user.username,
                    'id': user.id,
                    'industryInvolvement': [], 
                    'interestAreas': [], 
                    'linkedinUrl': None, 
                    'occupationalAreas': [], 
                    'techstack': []
                    }
                }


    def create_and_teardown_users(test_client, db:SQLAlchemy, num_users=1):
        users = []
        # Get the last inserted ID in the User table
        last_id = db.session.query(func.max(User.id)).scalar()
        if last_id is None: last_id = 0

        for idx in range(last_id, last_id + num_users):
            stub = idx
            user = User(
                username=f'testuser{stub}', 
                email=f'test{stub}@example.com', 
                full_name=f'Test User {stub}',
                current_company='Test Labs',
                user_vendor_associations = [],
                subscribed_discuss_categories = [],
                password=generate_password_hash('password')
                )
            db.session.add(user)
            users.append(user)
        db.session.commit()
        yield users
        for user in users:
            db.session.delete(user)
        db.session.commit()
    
    def create_and_teardown_techstack(test_client, user:User, db:SQLAlchemy, num_vendors:int):
        """Associate mock vendors with a user techstack. Connects vendor ids in range(1,num_vendors) to user"""
        print("WHAT THE FUCK")
        db.session.add("Something nonsensical")
        db.session.commit()
        max_vendors = len(DataInserter().vendors)

        if num_vendors > max_vendors: 
            raise ValueError(f"Error in create_and_teardown_techstack. num_vendors({num_vendors}) exceeds total available({max_vendors})")
        
        vendors = [PublicVendor(id=i) for i in range(1, num_vendors + 1)]
        user_vendor_associations = [UserPublicVendor(user_id=user.id, vendor_id=vendor.id) for vendor in vendors]
        print("Adding techstack")
        db.session.add_all(user_vendor_associations)
        db.session.commit()
        yield user_vendor_associations
        print("Deleting techstack")
        for vendor in user_vendor_associations:
            db.session.delete(vendor)
        db.session.commit()
    
    def endorse_mock_user(test_client, db:SQLAlchemy, endorsing_user:User, endorsee_user:User, vendor_id:int):
        endorsement = UserPublicVendorEndorsement(endorser_user_id=endorsing_user.id, endorsee_user_id=endorsee_user.id, vendor_id=vendor_id)
        db.session.add(endorsement)
        db.session.commit()
        yield endorsement
        db.session.delete(endorsement)
        db.session.commit()