import pymysql
import pymysql.cursors
class Post:
    def __init__(
            self,
            author_id,
            title,
            body,
            category_names = [],
            category_ids = [],
            tagged_vendor_names = [],
            tagged_vendor_ids = [],
            is_anonymous = False,
            post_id = -1,
            creation_time = None,
            update_time = None
    ):
        self.author_id = author_id
        self.title = title
        self.body = body
        self.category_names = category_names
        self.category_ids = category_ids
        self.tagged_vendor_names = tagged_vendor_names
        self.tagged_vendor_ids = tagged_vendor_ids
        self.is_anonymous = is_anonymous
        self.post_id = post_id
        self.creation_time = creation_time
        self.update_time = update_time
    
    @classmethod
    def post_from_post_id(cls, cursor, post_id):
        # Retrieve general post information
        cursor.execute(
            """SELECT id, user_id, is_anonymous, title, body, creation_time, update_time 
            FROM Post WHERE id = %s""",
            (post_id)
        )
        post_info = cursor.fetchone()
        if not post_info: return None
        post = cls(
            author_id = post_info['user_id'],
            title = post_info['title'],
            body = post_info['body'],
            creation_time = post_info['creation_time'],
            update_time = post_info['update_time'],
            is_anonymous = post_info['is_anonymous'],
            post_id = post_id
        )
        post.category_names, post.category_ids = post.retrieve_post_category_names_and_ids(cursor, post_id)
        post.tagged_vendor_names, post.tagged_vendor_ids = post.retrieve_tagged_vendor_names_and_ids(cursor, post_id)
        return post
    
    @classmethod
    def upvote_post_with_id(cursor, user_id, post_id):
        cursor.execute("""
            INSERT INTO PostUpvote (post_id, user_id)
            VALUES (%s, %s)
        """, (post_id, user_id))
    
    @classmethod
    def remove_upvote_post_with_id(cursor, user_id, post_id):
        # Delete upvote from the PostUpvote table
        cursor.execute("""
            DELETE FROM PostUpvote
            WHERE user_id = %s AND post_id = %s
        """, (user_id, post_id))

    @classmethod
    def is_post_liked_by_user(cursor, user_id, post_id):
        cursor.execute("""
            SELECT id FROM PostUpvote 
            WHERE user_id = %s AND post_id = %s
        """, (user_id, post_id))
        if cursor.fetchone():
            return True


    def retrieve_post_category_names_and_ids(self, cursor, post_id):
        # Grab category ids
        cursor.execute(
            """SELECT category_id FROM PostDiscussCategory WHERE post_id = %s""",
            (post_id)
        )
        categories = cursor.fetchall()
        category_names = []
        category_ids = []
        for item in categories:
            category_id = item['category_id']
            category_ids.append(category_id)
            cursor.execute("""SELECT category_name FROM DiscussCategory WHERE id = %s""",
                           (category_id)
                        )
            category_name = cursor.fetchone()['category_name']
            category_names.append(category_name)
        
        return category_names, category_ids

    def retrieve_tagged_vendor_names_and_ids(self, cursor, post_id):
        # Grab vendor ids
        cursor.execute(
            """SELECT vendor_id FROM PostDiscoverVendor WHERE post_id = %s""",
            (post_id)
        )
        vendors = cursor.fetchall()
        vendor_names = []
        vendor_ids = []
        for item in vendors:
            vendor_id = item['vendor_id']
            vendor_ids.append(vendor_id)
            cursor.execute("""SELECT vendor_name FROM DiscoverVendor WHERE id = %s""",
                           (vendor_id)
                        )
            vendor_name = cursor.fetchone()['vendor_name']
            vendor_names.append(vendor_name)
        
        return vendor_names, vendor_ids
    
    def create_post(self, cursor):
        # Insert post into database
        cursor.execute("""
            INSERT INTO Post (user_id, title, body, is_anonymous) 
            VALUES (%s, %s, %s, %s)
        """, (self.author_id, self.title, self.body, self.is_anonymous))
        self.post_id = cursor.lastrowid
        self.link_post_to_categories(cursor)
        self.link_post_to_vendors(cursor)
    
    def edit_post(self, cursor,
                 new_title = None,
                 new_body = None,
                 new_category_names = None,
                 new_vendor_names = None):
        
        # Edit post information
        if new_title:
            cursor.execute("""
                UPDATE Post SET title = COALESCE(%s, title),
                                update_time = CURRENT_TIMESTAMP(3)
                WHERE id = %s AND user_id = %s
            """, (new_title, self.post_id, self.author_id))
            self.title = new_title

        if new_body:
            cursor.execute("""
                UPDATE Post SET body = COALESCE(%s, body),
                                update_time = CURRENT_TIMESTAMP(3)
                WHERE id = %s AND user_id = %s
            """, (new_body, self.post_id, self.author_id))
        
        if new_category_names:
            # Add new categories (TODO: Efficiency)
            for category_name in new_category_names - self.category_names:
                cursor.execute("SELECT id FROM DiscussCategory WHERE category_name = %s", (category_name,))
                category = cursor.fetchone()
                if category:
                    cursor.execute("""
                        INSERT INTO PostDiscussCategory (post_id, category_id) 
                        VALUES (%s, %s)
                    """, (self.post_id, category['id']))
            
            # Delete old categories (TODO: Efficiency)
            for category_name in self.category_names - new_category_names:
                cursor.execute("SELECT id FROM DiscussCategory WHERE category_name = %s", (category_name,))
                category = cursor.fetchone()
                if category:
                    cursor.execute("""
                        DELETE FROM PostDiscussCategory 
                        WHERE post_id = %s AND category_id = %s
                    """, (self.post_id, category['id']))
            
            self.category_names, self.category_ids = self.retrieve_post_category_names_and_ids(cursor, self.post_id)
        
        if new_vendor_names:
            # Add new vendors (TODO: Efficiency)
            for vendor_name in new_vendor_names - self.tagged_vendor_names:
                cursor.execute("SELECT id FROM DiscoverVendor WHERE vendor_name = %s", (vendor_name,))
                vendor = cursor.fetchone()
                if vendor:
                    cursor.execute("""
                        INSERT INTO PostDiscoverVendor (post_id, vendor_id) 
                        VALUES (%s, %s)
                    """, (self.post_id, vendor['id']))
            
            # Delete old vendors (TODO: Efficiency)
            for vendor_name in self.tagged_vendor_names - new_vendor_names:
                cursor.execute("SELECT id FROM DiscoverVendor WHERE vendor_name = %s", (vendor_name,))
                vendor = cursor.fetchone()
                if vendor:
                    cursor.execute("""
                        DELETE FROM PostDiscoverVendor
                        WHERE post_id = %s AND vendor_id = %s
                    """, (self.post_id, vendor['id']))
            
            self.tagged_vendor_names, self.tagged_vendor_ids = self.retrieve_tagged_vendor_names_and_ids(cursor, self.post_id)

    def link_post_to_categories(self, cursor):
        # Link post to categories
        for category_name in self.category_names:
            cursor.execute("SELECT id FROM DiscussCategory WHERE category_name = %s", (category_name,))
            category = cursor.fetchone()
            if category:
                cursor.execute("""
                    INSERT INTO PostDiscussCategory (post_id, category_id) 
                    VALUES (%s, %s)
                """, (self.post_id, category['id']))
    
    def link_post_to_vendors(self, cursor):
        # Link post to vendors
        for vendor_name in self.tagged_vendor_names:
            cursor.execute("SELECT id FROM DiscoverVendor WHERE vendor_name = %s", (vendor_name,))
            vendor = cursor.fetchone()
            if vendor:
                cursor.execute("""
                    INSERT INTO PostDiscoverVendor(post_id, vendor_id) 
                    VALUES (%s, %s)
                """, (self.post_id, vendor['id']))


