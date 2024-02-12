import pymysql

# Database conn details
DB_HOST = 'realtalktechrdsstack-realtalktechdbinstance-c7ciisdczocf.cnqm62ueodz0.us-east-1.rds.amazonaws.com'
DB_USER = 'admin'
DB_PASSWORD = 'ReallyRealAboutTech123!'
DB_NAME = 'RealTalkTechDB'

class DataBuilder:
    def __init__(self):
        # Establish database connection and call methods to insert data
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        self.cursor = conn.cursor()
        self.test_user_ids = []
        self.discuss_categories = [
            "AI", "Engineering", "Operations", "Marketing", "Sales", "Customer Success",
            "Data", "Product", "HR & Talent", "Finance", "Leadership/Exec", "Founder",
            "Community"
        ]
        self.discuss_category_ids = []
        self.discover_categories = [
            "Sales Tools", "Marketing", "Analytics Tools & Software", "CAD & PLM", "Collaboration & Productivity",
            "Commerce", "Content Management", "Customer Service", "Data Privacy", "Design", "Development",
            "Digital Advertising Tech", "ERP", "Governance, Risk & Compliance", "Hosting", "HR", "IT Infrastructure",
            "IT Management", "Security", "Supply Chains & Logistics", "Vertical Industry"
        ]
        self.discover_category_ids = []
        self.vendors = {
            'Salesforce': {
                'vendor_name': "Salesforce",
                'vendor_type': "CRM Software",
                'description': "Salesforce forces sales",
                'vendor_hq': "Somewhere",
                'vendor_homepage_url': "https://www.salesforce.com/",
                'vendor_logo_url': "https://vendor-logos-bucket.s3.amazonaws.com/vendorLogos/Salesforce-logo.jpg"
            },

            'HubSpot': {
                'vendor_name': "HubSpot",
                'vendor_type': "Inbound Marketing and Sales Software",
                'description': "The spot for all the hubs",
                'vendor_hq': "Over the Rainbow",
                'vendor_homepage_url': "https://www.hubspot.com/",
                'vendor_logo_url': "https://vendor-logos-bucket.s3.amazonaws.com/vendorLogos/HubSpot-logo.jpg"
            },

            'Zendesk Sell': {
                'vendor_name': "Zendesk Sell",
                'vendor_type': "Sales CRM",
                'description': "Feng Shui desks for selling",
                'vendor_hq': "Beyond the Sea",
                'vendor_homepage_url': "https://www.zendesk.com/",
                'vendor_logo_url': "https://vendor-logos-bucket.s3.amazonaws.com/vendorLogos/Zendesk_Sell-logo.jpg"
            }                        
        }
        self.vendor_ids = []
        self.industries = [
            "AdTech", "Angel or VC Firm", "AI", "Automation", "Big Data", "Biotech", "Blockchain",
            "Business Intelligence", "Cannabis", "Cloud", "Consulting", "Web/Internet", "Crypto",
            "Cybersecurity", "Data Privacy", "Database", "eCommerce", "Edtech", "FinTech", "Gaming",
            "Healthtech", "HR Tech", "IaaS", "Insurance", "IoT", "Legal Tech", "Logistics", "Machine Learning",
            "Manufacturing", "MarTech", "Metaverse", "Mobile", "Music", "Natural Language Processing",
            "NFT", "Payments", "Pharmaceutical", "Procurement", "Professional Services", "Real Estate", "Sales",
            "Software", "Sports", "Travel", "Web3", "Other"
        ]
        self.industry_ids = []
        self.interest_areas = [
            "Sales Tools", "Marketing", "Analytics Tools & Software", "CAD & PLM", "Collaboration & Productivity",
            "Commerce", "Customer Service", "Data Privacy", "Design", "Development", "Digital Advertising",
            "ERP", "Governance, Risk & Compliance", "Hosting", "HR", "IT Infrastructure", "IT Management",
            "Office", "Security", "Supply Chain & Logistics", "Vertical Industry", "Collaboration",
            "Customer Management", "Revenue Operations", "Payments", "Accounting", "Learning Management System",
            "Robotic Process Automation", "Artificial Intelligence"
        ]
        self.interest_area_ids = []

        try:
            self.insert_test_users()
            self.insert_discuss_categories()
            self.insert_discover_categories()
            self.insert_test_vendors()
            self.insert_post_1()
            self.insert_post_2()
            self.insert_post_3()
            self.insert_post_4()
            self.insert_industries()
            self.insert_interest_areas()

        finally:
            conn.commit()
            self.cursor.close()
            conn.close()

    def insert_test_users(self):
        """Inserts four test users"""
        names = ["Elon Gates", "Bill Musk", "Mary Barra", "Kamala Clinton"]
        employers = ["SuperchargedSoftware", "MacroAdvanced", "General Autos", "Capitol Tech"]
        for idx, name in enumerate(names):
            username = name.replace(" ", "").lower()
            email = username.join("@example.com")
            current_company = employers[idx]

            self.cursor.execute(
                """INSERT INTO User (full_name, username, password, current_company, email) 
                VALUES (%s, %s, 'password', %s, %s)""", (name, username, current_company, email)
            )
            self.cursor.execute("SELECT LAST_INSERT_ID()")
            user_id = self.cursor.fetchone()['LAST_INSERT_ID()']
            self.test_user_ids.append(user_id)

    def insert_discuss_categories(self):
        """Insert categories according to Figma Designs"""
        for name in self.discuss_categories:
            self.cursor.execute("INSERT INTO DiscussCategory (category_name) VALUES (%s)", (name,))
            self.cursor.execute("SELECT LAST_INSERT_ID()")
            category_id = self.cursor.fetchone()['LAST_INSERT_ID()']
            self.discuss_category_ids.append(category_id)
    
    def insert_discover_categories(self):
        """Inserting just the sales category, for now"""
        for category in self.discover_categories:
            self.cursor.execute(
                "INSERT INTO DiscoverCategory (category_name) VALUES (%s)", 
                (category))
            self.cursor.execute("SELECT LAST_INSERT_ID()")
            vendor_category_id = self.cursor.fetchone()['LAST_INSERT_ID()']
            self.discover_category_ids.append(vendor_category_id)
    
    def insert_industries(self):
        for industry in self.industries:
            self.cursor.execute(
                """INSERT INTO Industry (industry_name) VALUES (%s)""",
                (industry)
            )
            self.cursor.execute("SELECT LAST_INSERT_ID()")
            industry_id = self.cursor.fetchone()['LAST_INSERT_ID()']            
            self.industry_ids.append(industry_id)
    
    def insert_interest_areas(self):
        for area in self.interest_areas:
            self.cursor.execute(
                """INSERT INTO InterestArea (interest_area_name) VALUES (%s)""",
                (area)
            )
            self.cursor.execute("SELECT LAST_INSERT_ID()")
            interest_area_id = self.cursor.fetchone()['LAST_INSERT_ID()']            
            self.interest_area_ids.append(interest_area_id)
    
    def insert_test_vendors(self):
        """Inserting Salesforce, HubSpot, Zendesk Sell"""
        for vendor, details in self.vendors.items():
            # Insert vendors into table
            self.cursor.execute(
                """INSERT INTO DiscoverVendor (vendor_name, vendor_type, description, vendor_hq, vendor_homepage_url, vendor_logo_url) 
                VALUES (%s, %s, %s, %s, %s, %s)""", 
                (details['vendor_name'], 
                 details['vendor_type'],
                 details['description'],
                 details['vendor_hq'],
                 details['vendor_homepage_url'],
                 details['vendor_logo_url']
                )
            )
            # Link vendors to categories
            self.cursor.execute("SELECT LAST_INSERT_ID()")
            vendor_id = self.cursor.fetchone()['LAST_INSERT_ID()']
            self.vendor_ids.append(vendor_id)
            self.cursor.execute(
                """INSERT INTO VendorDiscoverCategory (vendor_id, category_id) VALUES (%s, %s)""", 
                (vendor_id, self.discover_category_ids[0])
            )
    
    def insert_post_1(self):
        """Inserts a post from Elon Gates, tags Salesforce, comments from Bill and Mary, Elon likes Bill's comment"""
        # Insert post
        self.cursor.execute(
            """INSERT INTO Post (user_id, is_anonymous, title, body) VALUES (%s, %s, %s, %s)""",
            (self.test_user_ids[0], False, "Salesforce is awesome", "I've sold so many cars.")
        )
        self.cursor.execute("SELECT LAST_INSERT_ID()")
        post_id = self.cursor.fetchone()['LAST_INSERT_ID()']

        # Tag Salesforce in post
        self.cursor.execute(
            """INSERT INTO PostDiscoverVendor (post_id, vendor_id) VALUES (%s,%s)""",
            (post_id, self.vendor_ids[0])
        )
        # Insert comment from Bill
        self.cursor.execute(
            """INSERT INTO Comment (post_id, user_id, comment_text) VALUES (%s, %s, %s)""",
            (post_id, self.test_user_ids[1], "Salesforce is a great tool!")
        )
        self.cursor.execute("SELECT LAST_INSERT_ID()")
        comment_id = self.cursor.fetchone()['LAST_INSERT_ID()']

        # Insert comment from Mary
        self.cursor.execute(
            """INSERT INTO Comment (post_id, user_id, comment_text) VALUES (%s, %s, %s)""",
            (post_id, self.test_user_ids[2], "Maybe I should try it so I can sell more cars too")
        )

        # Elon likes Bill's comment
        self.cursor.execute(
            """INSERT INTO CommentUpvote (comment_id, user_id) VALUES (%s, %s)""",
            (comment_id, self.test_user_ids[0])
        )

    def insert_post_2(self):
        """Inserts a post from Elon Gates about HubSpot, with comments and likes"""
        # Insert post about HubSpot
        self.cursor.execute(
            """INSERT INTO Post (user_id, is_anonymous, title, body) VALUES (%s, %s, %s, %s)""",
            (self.test_user_ids[0], False, "HubSpot Revolution", "HubSpot has changed the way we market!")
        )
        self.cursor.execute("SELECT LAST_INSERT_ID()")
        post_id = self.cursor.fetchone()['LAST_INSERT_ID()']

        # Tag HubSpot in post
        self.cursor.execute(
            """INSERT INTO PostDiscoverVendor (post_id, vendor_id) VALUES (%s, %s)""",
            (post_id, self.vendor_ids[1])
        )

        # Comments and likes
        self.insert_comment_and_like(post_id, self.test_user_ids[2], "HubSpot is indeed a game-changer!", self.test_user_ids[1])

    def insert_post_3(self):
        """Inserts an anonymous post by Elon Gates, no tags, with comments"""
        # Insert anonymous post
        self.cursor.execute(
            """INSERT INTO Post (user_id, is_anonymous, title, body) VALUES (%s, %s, %s, %s)""",
            (self.test_user_ids[0], True, "Anonymous Insights", "What are your thoughts on the future of AI in sales?")
        )
        self.cursor.execute("SELECT LAST_INSERT_ID()")
        post_id = self.cursor.fetchone()['LAST_INSERT_ID()']

        # Comments
        self.insert_comment(post_id, self.test_user_ids[1], "AI is going to be crucial in understanding customer needs.")

    def insert_post_4(self):
        """Inserts a post from Elon Gates about Zendesk Sell, with comments and likes"""
        # Insert post about Zendesk Sell
        self.cursor.execute(
            """INSERT INTO Post (user_id, is_anonymous, title, body) VALUES (%s, %s, %s, %s)""",
            (self.test_user_ids[0], False, "Zendesk Sell's Impact", "Our sales team loves Zendesk Sell!")
        )
        self.cursor.execute("SELECT LAST_INSERT_ID()")
        post_id = self.cursor.fetchone()['LAST_INSERT_ID()']

        # Tag Zendesk Sell in post
        self.cursor.execute(
            """INSERT INTO PostDiscoverVendor (post_id, vendor_id) VALUES (%s, %s)""",
            (post_id, self.vendor_ids[2])
        )

        # Comments and likes
        self.insert_comment_and_like(post_id, self.test_user_ids[3], "It's a superb tool!", self.test_user_ids[0])

    def insert_comment(self, post_id, user_id, text):
        """Helper function to insert a comment"""
        self.cursor.execute(
            """INSERT INTO Comment (post_id, user_id, comment_text) VALUES (%s, %s, %s)""",
            (post_id, user_id, text)
        )

    def insert_comment_and_like(self, post_id, commenter_id, comment_text, liker_id):
        """Helper function to insert a comment and a like"""
        self.insert_comment(post_id, commenter_id, comment_text)
        self.cursor.execute("SELECT LAST_INSERT_ID()")
        comment_id = self.cursor.fetchone()['LAST_INSERT_ID()']

        # Insert like
        self.cursor.execute(
            """INSERT INTO CommentUpvote (comment_id, user_id) VALUES (%s, %s)""",
            (comment_id, liker_id)
        )

if __name__ == '__main__':
    # Establish database connection and call methods to insert data
    databuilder = DataBuilder()
