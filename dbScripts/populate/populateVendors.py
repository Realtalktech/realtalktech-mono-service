import pandas as pd
import pymysql

# Database conn details
HOST = 'realtalktechrdsstack-realtalktechdbinstance-c7ciisdczocf.cnqm62ueodz0.us-east-1.rds.amazonaws.com'
USERNAME = 'admin'
PASSWORD = 'ReallyRealAboutTech123!'
DATABASE = 'RealTalkTechDB'

# Establish database connection
connection = pymysql.connect(host=HOST, user=USERNAME, password=PASSWORD, db=DATABASE)
cursor = connection.cursor()


# Load the CSV file
df = pd.read_csv('dbScripts/data/discoverVendors_v1.csv')

# Iterate over each category
for category in df.columns:
    # Insert category into DiscoverCategory
    cursor.execute("INSERT IGNORE INTO DiscoverCategory (category_name) VALUES (%s)", (category,))
    connection.commit()

    # Get the category ID
    cursor.execute("SELECT id FROM DiscoverCategory WHERE category_name = %s", (category,))
    category_id = cursor.fetchone()[0]

    # Iterate over each vendor in the category
    for vendor in df[category].dropna():
        # Insert vendor into DiscoverVendor and PublicVendor
        cursor.execute("INSERT IGNORE INTO DiscoverVendor (vendor_name) VALUES (%s)", (vendor,))
        cursor.execute("INSERT IGNORE INTO PublicVendor (vendor_name) VALUES (%s)", (vendor,))
        connection.commit()

        # Get the vendor ID
        cursor.execute("SELECT id FROM DiscoverVendor WHERE vendor_name = %s", (vendor,))
        vendor_id = cursor.fetchone()[0]

        # Link vendor to category in VendorDiscoverCategory
        cursor.execute("""
            INSERT IGNORE INTO VendorDiscoverCategory (vendor_id, category_id)
            VALUES (%s, %s)
        """, (vendor_id, category_id))
        connection.commit()

# Close the connection
cursor.close()
connection.close()
