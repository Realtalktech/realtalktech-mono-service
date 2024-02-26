import sqlite3

class Databuilder:
    def __init__():
        pass

    def init_test_database():
        # Connect to test database, specify the path to SQLite test database file
        connection = sqlite3.connect('tests/sqlite/test_database.db')
        cursor = connection.cursor()

        # SQLite does not:
            # Enforce the length of VARCHAR 
            # Support DATETIME(3)
            # Support AUTO_INCREMENT
        # Simplify these to TEXT and DATETIME, and just INTEGER PRIMARY KEY respectively for SQLite.
        # SQLite 'INTEGER PRIMARY KEY' auto-increments

        # Recreate the tables for the test database
        # Note: Removed AUTO_INCREMENT, changed DATETIME(3) to DATETIME, and VARCHAR to TEXT for compatibility

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
