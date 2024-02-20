import pymysql
import logging

# Database conn details
DB_HOST = 'realtalktechrdsstack-realtalktechdbinstance-c7ciisdczocf.cnqm62ueodz0.us-east-1.rds.amazonaws.com'
DB_USER = 'admin'
DB_PASSWORD = 'ReallyRealAboutTech123!'
DB_NAME = 'RealTalkTechDB'


# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        self.industries = [
            "AdTech", "Angel or VC Firm", "AI", "Automation", "Big Data", "Biotech", "Blockchain",
            "Business Intelligence", "Cannabis", "Cloud", "Consulting", "Web/Internet", "Crypto",
            "Cybersecurity", "Data Privacy", "Database", "eCommerce", "Edtech", "FinTech", "Gaming",
            "Healthtech", "HR Tech", "IaaS", "Insurance", "IoT", "Legal Tech", "Logistics", "Machine Learning",
            "Manufacturing", "MarTech", "Metaverse", "Mobile", "Music", "Natural Language Processing",
            "NFT", "Payments", "Pharmaceutical", "Procurement", "Professional Services", "Real Estate", "Sales",
            "Software", "Sports", "Travel", "Web3", "Other"
        ]
        self.interest_areas = [
            "Sales Tools", "Marketing", "Analytics Tools & Software", "CAD & PLM", "Collaboration & Productivity",
            "Commerce", "Customer Service", "Data Privacy", "Design", "Development", "Digital Advertising",
            "ERP", "Governance, Risk & Compliance", "Hosting", "HR", "IT Infrastructure", "IT Management",
            "Office", "Security", "Supply Chain & Logistics", "Vertical Industry", "Collaboration",
            "Customer Management", "Revenue Operations", "Payments", "Accounting", "Learning Management System",
            "Robotic Process Automation", "Artificial Intelligence"
        ]

        try:
            self.insert_test_users()
            self.insert_post_1()
            self.insert_post_2()
            self.insert_post_3()
            self.insert_post_4()

        finally:
            conn.commit()
            self.cursor.close()
            conn.close()

    def insert_test_users(self):
        """Inserts four test users"""
        names = ["Elon Gates", "Bill Musk", "Mary Barra", "Kamala Clinton"]
        employers = ["SuperchargedSoftware", "MacroAdvanced", "General Autos", "Capitol Tech"]
        for i, name in enumerate(names):
            username = name.replace(" ", "").lower()
            email = username.join("@example.com")
            current_company = employers[i]
            
            quarter_size = len(self.discuss_categories) // len(names)
            user_discuss_categories = self.discuss_categories[i * quarter_size: (i + 1) * quarter_size]
            
            quarter_size = len(self.industries) // len(names)
            user_industries = self.industries[i * quarter_size: (i + 1) * quarter_size]
            
            quarter_size = len(self.interest_areas) // len(names)
            user_interest_areas = self.interest_areas[i * quarter_size: (i + 1) * quarter_size]

            self.cursor.execute(
                """INSERT INTO User (full_name, username, password, current_company, email) 
                VALUES (%s, %s, 'password', %s, %s)""", (name, username, current_company, email)
            )

            self.cursor.execute("SELECT LAST_INSERT_ID()")
            user_id = self.cursor.fetchone()['LAST_INSERT_ID()']
            self.test_user_ids.append(user_id)

            # Subscribe user to categories
            for category in user_discuss_categories:
                self.cursor.execute("""SELECT id FROM DiscussCategory WHERE category_name = %s""", (category))
                category_id = self.cursor.fetchone().get('id')
                if category_id:
                    self.cursor.execute("""INSERT INTO UserDiscussCategory (user_id, category_id) VALUES (%s, %s)""", (user_id, category_id))
                else:
                    logging.error("Could not find category named: %s", (category))
            
            # Subscribe user to industries
            for industry in user_industries:
                self.cursor.execute("""SELECT id FROM Industry WHERE industry_name = %s""", (industry))
                industry_id = self.cursor.fetchone().get('id')
                if industry_id:
                    self.cursor.execute("""INSERT INTO UserIndustry (user_id, industry_id) VALUES (%s, %s)""", (user_id, industry_id))
                else:
                    logging.error("Could not find industry named: %s", (industry))

            # Subscribe user to interest area
            for area in user_interest_areas:
                self.cursor.execute("""SELECT id FROM InterestArea WHERE interest_area_name = %s""", (area))
                area_id = self.cursor.fetchone().get('id')
                if area_id:
                    self.cursor.execute("""INSERT INTO UserIndustry (user_id, industry_id) VALUES (%s, %s)""", (user_id, area_id))
                else:
                    logging.error("Could not find interest_area named: %s", (area))


    
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
            (post_id, 2)
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
            """INSERT INTO CommentUpvote (comment_id, is_downvote, user_id) VALUES (%s, %s, %s)""",
            (comment_id, False, self.test_user_ids[0])
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
            (post_id, 5)
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
            (post_id, 42)
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
            """INSERT INTO CommentUpvote (comment_id, is_downvote, user_id) VALUES (%s, %s, %s)""",
            (comment_id, False, liker_id)
        )

if __name__ == '__main__':
    # Establish database connection and call methods to insert data
    databuilder = DataBuilder()
