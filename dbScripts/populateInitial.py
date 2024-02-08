import pymysql

# Database conn details
DB_HOST = 'realtalktechrdsstack-realtalktechdbinstance-c7ciisdczocf.cnqm62ueodz0.us-east-1.rds.amazonaws.com'
DB_USER = 'admin'
DB_PASSWORD = 'ReallyRealAboutTech123!'
DB_NAME = 'RealTalkTechDB'

class DataBuilder:
    def insert_test_users(self, cursor):
        """Inserts four test users"""
        names = ["Elon Gates", "Bill Musk", "Mary Barra", "Kamala Clinton"]
        employers = ["SuperchargedSoftware", "MacroAdvanced", "General Autos", "Capitol Tech"]
        self.test_user_ids = []
        for idx, name in enumerate(names):
            username = name.replace(" ", "").lower()
            email = username.join("@example.com")
            current_company = employers[idx]

            cursor.execute(
                """INSERT INTO User (full_name, username, password, current_company, email) 
                VALUES (%s, %s, 'password', %s, %s)""", (name, username, current_company, email)
            )
            cursor.execute("SELECT LAST_INSERT_ID()")
            user_id = cursor.fetchone()['LAST_INSERT_ID()']
            self.test_user_ids.append(user_id)

    def insert_categories(self,cursor):
        """Insert categories according to Figma Designs"""
        category_names = [
            "AI", "Engineering", "Operations", "Marketing", "Sales", "Customer Success",
            "Data", "Product", "HR & Talent", "Finance", "Leadership/Exec", "Founder",
            "Community"
        ]

        # Insert categories
        self.category_ids = []
        for name in category_names:
            cursor.execute("INSERT INTO Category (category_name) VALUES (%s)", (name,))
            cursor.execute("SELECT LAST_INSERT_ID()")
            category_id = cursor.fetchone()['LAST_INSERT_ID()']
            self.category_ids.append(category_id)
    
    def insert_discover_categories(self,cursor):
        """Inserting just the sales category, for now"""
        categories = ["Sales Tools"]
        descriptions = ["Tools for Sales"]
        self.vendor_category_ids = []
        for idx,category in enumerate(categories):
            cursor.execute(
                "INSERT INTO DiscoverCategory (category_name, description) VALUES (%s, %s)", 
                (category, descriptions[idx]))
            cursor.execute("SELECT LAST_INSERT_ID()")
            vendor_category_id = cursor.fetchone()['LAST_INSERT_ID()']
            self.vendor_category_ids.append(vendor_category_id)
    
    def insert_test_vendors(self, cursor):
        """Inserting Salesforce, HubSpot, Zendesk Sell"""
        self.vendor_names = ['Salesforce', 'HubSpot', 'Zendesk Sell']
        vendors = {
            'Salesforce': {
                'vendor_name': "Salesforce",
                'vendor_type': "CRM Software",
                'description': "Salesforce forces sales",
                'vendor_hq': "Somewhere"
            },

            'HubSpot': {
                'vendor_name': "HubSpot",
                'vendor_type': "Inbound Marketing and Sales Software",
                'description': "The spot for all the hubs",
                'vendor_hq': "Over the Rainbow"
            },

            'Zendesk Sell': {
                'vendor_name': "Zendesk Sell",
                'vendor_type': "Sales CRM",
                'description': "Feng Shui desks for selling",
                'vendor_hq': "Beyond the Sea"
            }                        
        }
        self.vendor_ids = []
        for name in self.vendor_names:
            # Insert vendors into table
            cursor.execute(
                """INSERT INTO DiscoverVendor (vendor_name, vendor_type, description, vendor_hq) 
                VALUES (%s, %s, %s, %s)""", 
                (vendors[name]['vendor_name'], 
                 vendors[name]['vendor_type'],
                 vendors[name]['description'],
                 vendors[name]['vendor_hq'])
            )
            # Link vendors to categories
            cursor.execute("SELECT LAST_INSERT_ID()")
            vendor_id = cursor.fetchone()['LAST_INSERT_ID()']
            self.vendor_ids.append(vendor_id)
            cursor.execute(
                """INSERT INTO DiscoverVendorCategory (vendor_id, category_id) VALUES (%s, %s)""", 
                (vendor_id, self.vendor_categories[0])
            )
            
    def insert_post_1(self, cursor):
        """Inserts a post from Elon Gates, tags Salesforce, comments from Bill and Mary, Elon likes Bill's comment"""
        # Insert post
        cursor.execute(
            """INSERT INTO Post (user_id, is_anonymous, title, body) VALUES (%s, %s, %s, %s)""",
            (self.test_user_ids[0], False, "Salesforce is awesome", "I've sold so many cars.")
        )
        cursor.execute("SELECT LAST_INSERT_ID()")
        post_id = cursor.fetchone()['LAST_INSERT_ID()']

        # Tag Salesforce in post
        cursor.execute(
            """INSERT INTO PostVendor (post_id, vendor_id) VALUES (%s,%s)""",
            (post_id, self.vendor_ids[0])
        )
        # Insert comment from Bill
        cursor.execute(
            """INSERT INTO Comment (post_id, user_id, comment_text) VALUES (%s, %s, %s)""",
            (post_id, self.test_user_ids[1], "Salesforce is a great tool!")
        )
        cursor.execute("SELECT LAST_INSERT_ID()")
        comment_id = cursor.fetchone()['LAST_INSERT_ID()']

        # Insert comment from Mary
        cursor.execute(
            """INSERT INTO Comment (post_id, user_id, comment_text) VALUES (%s, %s, %s)""",
            (post_id, self.test_user_ids[2], "Maybe I should try it so I can sell more cars too")
        )

        # Elon likes Bill's comment
        cursor.execute(
            """INSERT INTO CommentUpvote (comment_id, user_id) VALUES (%s, %s)""",
            (comment_id, self.test_user_ids[0])
        )

if __name__ == '__main__':
    # Establish database conn
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    insert_notional_data(cursor)
    conn.commit()
    cursor.close()
    conn.close()
    cursor.close()