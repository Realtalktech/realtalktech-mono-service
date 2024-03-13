import pymysql
import pprint

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
        self.discuss_categories = [
            "Artificial Intelligence", "Engineering", "Operations", "Marketing", "Sales", "Customer Success",
            "Data", "Product", "HR & Talent", "Finance", "Leadership/Exec", "Founder",
            "Community"
        ]
        self.discuss_category_ids = []
        self.discuss_category_mappings = {}
        self.industries = [
            "AdTech", "Angel or VC Firm", "Artificial Intelligence", "Automation", "Big Data", "Biotech", "Blockchain",
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
            self.insert_discuss_categories()
            self.insert_industries()
            self.insert_interest_areas()

        finally:
            conn.commit()
            self.cursor.close()
            conn.close()

    def insert_discuss_categories(self):
        """Insert categories according to Figma Designs"""
        for name in self.discuss_categories:
            self.cursor.execute("INSERT INTO DiscussCategory (category_name) VALUES (%s)", (name,))
            self.cursor.execute("SELECT LAST_INSERT_ID()")
            category_id = self.cursor.fetchone()['LAST_INSERT_ID()']
            self.discuss_category_ids.append(category_id)
            self.discuss_category_mappings[name] = category_id

    
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

if __name__ == '__main__':
    # Establish database connection and call methods to insert data
    databuilder = DataBuilder()
