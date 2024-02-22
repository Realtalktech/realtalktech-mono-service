import csv
import pymysql
import boto3
from boto3 import s3
import logging
from os import path
import glob

# Database conn details
DB_HOST = 'realtalktechrdsstack-realtalktechdbinstance-c7ciisdczocf.cnqm62ueodz0.us-east-1.rds.amazonaws.com'
DB_USER = 'admin'
DB_PASSWORD = 'ReallyRealAboutTech123!'
DB_NAME = 'RealTalkTechDB'


# Configuration
AWS_ACCESS_KEY_ID = 'AKIAQ3EGPNN5DV6E4BAZ'
AWS_SECRET_ACCESS_KEY = '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'
S3_BUCKET = 'vendor-logos-bucket'

# Paths
CATEGORY_ICON_PATH = 'dbScripts/data/discover_logo_prod'
VENDOR_LOGO_PATH = 'dbScripts/data/vendor_logo_prod'
CSV_PATH = 'dbScripts/data/discoverVendors_v4.csv'

IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'svg']  # Add more as needed

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Category Names
discover_categories = {
    "Sales Tools": {
        'id': 1,
        'name': 'Sales Tools'
    },
    "Marketing": {
        'id': 2,
        'name': 'Marketing'
    }, 
    "Analytics Tools & Software": {
        'id': 3,
        'name': 'Analytics Tools & Software'
    }, 
    "CAD & PLM": {
        'id': 4,
        'name': 'CAD & PLM'
    },
    "Collaboration & Productivity": {
        'id': 5,
        'name': 'Collaboration & Productivity'
    },
    "Commerce": {
        'id': 6,
        'name': 'Commerce'
    },
    "Content Management": {
        'id': 7,
        'name': 'Content Management'
    },
    "Customer Service": {
        'id': 8,
        'name': 'Customer Service'
    }, 
    "Data Privacy": {
        'id': 9,
        'name': 'Data Privacy'
    }, 
    "Design": {
        'id': 10,
        'name': 'Design'
    },
    "Development": {
        'id': 11,
        'name': 'Development'
    },
    "Digital Advertising Tech":{
        'id': 12,
        'name': 'Digital Advertising Tech'
    }, 
    "ERP": {
        'id': 13,
        'name': 'ERP'
    },
    "Governance, Risk & Compliance" : {
        'id': 14,
        'name': 'Governance, Risk & Compliance'
    }, 
    "Hosting": {
        'id': 15,
        'name': 'Hosting'
    }, 
    "HR": {
        'id': 16,
        'name': 'HR'
    }, 
    "IT Infrastructure": {
        'id': 17,
        'name': 'IT Infrastructure'
    },
    "IT Management": {
        'id': 18,
        'name': 'IT Management'
    }, 
    "Security": {
        'id': 19,
        'name': 'Security'
    }, 
    "Supply Chains & Logistics": {
        'id': 20,
        'name': 'Supply Chains & Logistics'
    }, 
    "Vertical Industry": {
        'id': 21,
        'name': 'Vertical Industry'
    }
}

# S3 Client
try:
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
except Exception as e:
    logging.error(f"Failed to create S3 client: {e}")
    exit(1)

# Database Connection
try:
    db = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    cursor = db.cursor()
except pymysql.MySQLError as e:
    logging.error(f"Failed to connect to database: {e}")
    exit(1)

def find_vendor_logo(vendor_name, vendor_logo_base_path):
    """Find the vendor logo with any extension."""
    for ext in IMAGE_EXTENSIONS:
        pattern = f"{vendor_name.replace('&', 'and').replace(',','').replace('.','-').replace(' ', '-').lower()}.{ext}"
        # logging.info(f"Searching logo for vendor {vendor_name} with filename {pattern}")
        vendor_logo_path = path.join(VENDOR_LOGO_PATH, pattern)
        if path.exists(vendor_logo_path):
            return vendor_logo_path
    return None  # If no files found

def upload_to_s3(file_path, category, file_name):
    """Upload a file to S3 and return the URL."""
    s3_path = f"{category}/{file_name}"
    try:
        s3.upload_file(file_path, S3_BUCKET, s3_path)
        return f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_path}"
    except boto3.exceptions.S3UploadFailedError as e:
        logging.error(f"Failed to upload {file_name} to S3: {e}")
        return None

def insert_discover_categories():
        # Insert Categories
        for category in discover_categories.keys():
            category_icon_filename = f"{category.replace('&', 'and').replace(',','').replace(' ', '-').lower()}.svg"
            # logging.info(f"Searching logo for category {category} with filename {category_icon_filename}")
            category_icon_path = path.join(CATEGORY_ICON_PATH, category_icon_filename)
            if path.exists(category_icon_path):
                category_icon_data = open(category_icon_path, 'r').read()
                cursor.execute("INSERT INTO DiscoverCategory (category_name, icon) VALUES (%s, %s) ON DUPLICATE KEY UPDATE icon = VALUES(icon)", (category, category_icon_data))
                db.commit()
            else:
                logging.warning(f"No icon found for category {category}")

def populate_database():
    with open(CSV_PATH, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            category = row['Category']
            name = row['Name']
            bio = row['Bio']
            hq = row['HQ']
            headcount = row['Headcount']
            homepage_url = row['URL']

            # Try to find and upload the vendor logo
            vendor_logo_filename = name.replace(' ', '-').lower()  # Adjust for actual file finding logic if necessary
            vendor_logo_path = find_vendor_logo(vendor_logo_filename, 'vendor_logo_prod/')
            if not vendor_logo_path or not path.exists(vendor_logo_path):
                logging.warning(f"No logo found for vendor {name}, vendor not uploaded")
                continue  # Skip this vendor and go to the next one

            # If we reach here, it means the logo exists
            vendor_logo_filename = path.basename(vendor_logo_path)
            vendor_logo_url = upload_to_s3(vendor_logo_path, 'vendor_logos_prod/' + category.replace(' ', '-').lower(), vendor_logo_filename)
            if not vendor_logo_url:
                logging.warning(f"Failed to upload logo for vendor {name}, vendor not uploaded")
                continue  # Skip this vendor and go to the next one

            # Now insert the vendor into DiscoverVendor
            cursor.execute("INSERT INTO DiscoverVendor (vendor_name, vendor_type, description, vendor_hq, total_employees, vendor_homepage_url, vendor_logo_url) VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE vendor_type = VALUES(vendor_type), description = VALUES(description), vendor_hq = VALUES(vendor_hq), total_employees = VALUES(total_employees), vendor_logo_url = VALUES(vendor_logo_url)", (name, category, bio, hq, headcount, homepage_url, vendor_logo_url))
            db.commit()
            discover_vendor_id = cursor.lastrowid

            # Now insert the vendor into PublicVendor
            cursor.execute("INSERT INTO PublicVendor (vendor_name, discover_vendor_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE discover_vendor_id = VALUES(discover_vendor_id)", (name, discover_vendor_id))
            db.commit()

            # Assuming 'discover_categories' is a dictionary mapping category names to their IDs
            category_id = discover_categories.get(category, {}).get('id', None)

            # Link Vendor and Category in DiscoverVendor
            if category_id and discover_vendor_id:
                cursor.execute("INSERT INTO VendorDiscoverCategory (vendor_id, category_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE vendor_id = VALUES(vendor_id), category_id = VALUES(category_id)", (discover_vendor_id, category_id))
                db.commit()
            else:
                logging.warning(f"Missing link between category {category} and vendor {name}")

if __name__ == "__main__":
    insert_discover_categories()
    populate_database()
