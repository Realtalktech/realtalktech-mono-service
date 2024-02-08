import pymysql

# Database conn details
DB_HOST = 'realtalktechrdsstack-realtalktechdbinstance-c7ciisdczocf.cnqm62ueodz0.us-east-1.rds.amazonaws.com'
DB_USER = 'admin'
DB_PASSWORD = 'ReallyRealAboutTech123!'
DB_NAME = 'RealTalkTechDB'

def insert_categories(cursor):
    category_names = [
        "AI", "Engineering", "Operations", "Marketing", "Sales", "Customer Success",
        "Data", "Product", "HR & Talent", "Finance", "Leadership/Exec", "Founder",
        "Community"
    ]

    # Insert categories



    #  """This will eventually be removed in lieu of calls to upcoming @POST methods."""
    # # Insert a test user
    # cursor.execute("INSERT INTO User (first_name, last_name, username, email, password) VALUES ('Test', 'User', 'test_user', 'test@example.com', 'password')")
    # cursor.execute("SELECT LAST_INSERT_ID()")
    # user_id = cursor.fetchone()['LAST_INSERT_ID()']

    # # Insert test categories
    # category_names = ['test1', 'test2', 'test3', 'test4']
    # category_ids = []
    # for name in category_names:
    #     cursor.execute("INSERT INTO Category (category_name) VALUES (%s)", (name,))
    #     cursor.execute("SELECT LAST_INSERT_ID()")
    #     category_id = cursor.fetchone()['LAST_INSERT_ID()']
    #     category_ids.append(category_id)
        
    #     if(name == 'test1' or name == 'test2'):
    #         # Associate user with the category
    #         cursor.execute("INSERT INTO UserCategory (user_id, category_id) VALUES (%s, %s)", (user_id, category_id))
    
    # # Insert test vendors
    # vendor_names = ['vendor1', 'vendor2', 'vendor3']
    # vendor_ids = []
    # for name in vendor_names:
    #     cursor.execute("INSERT INTO DiscoverVendor (vendor_name, vendor_type, description) VALUES (%s, 'Experts in API Testing', 'Experts in API Testing')", (name))
    #     cursor.execute("SELECT LAST_INSERT_ID()")
    #     vendor_id = cursor.fetchone()['LAST_INSERT_ID()']
    #     vendor_ids.append(vendor_id)

    # # Insert mock posts in each vendor and category
    # post_ids = []
    # postNum = 1
    # for vendor_id in vendor_ids:
    #     for category_id in category_ids:
    #         for i in range(5):  # 5 posts per vendor per category (5 * 3 * 4 = 60 Total Posts)
    #             cursor.execute("INSERT INTO Post (user_id, title, body) VALUES (%s, 'Mock title %s', 'Mock body %s')", (user_id, postNum, postNum))
    #             cursor.execute("SELECT LAST_INSERT_ID()")
    #             post_id = cursor.fetchone()['LAST_INSERT_ID()']
    #             post_ids.append(post_id)

    #             # Link post to category
    #             cursor.execute("INSERT INTO PostCategory (post_id, category_id) VALUES (%s, %s)", (post_id, category_id))

    #             # Link post to vendor
    #             cursor.execute("INSERT INTO PostVendor (post_id, vendor_id) VALUES (%s, %s)", (post_id, vendor_id))

    #             postNum = postNum + 1

    # # Insert 20 mock comments into the first post
    # commentPost = post_ids[0]
    # for i in range(20):
    #     cursor.execute("INSERT INTO Comment (post_id, user_id, comment_text) VALUES (%s, %s, 'Mock Comment %s')", (commentPost, user_id, i + 1))

    return False

if __name__ == '__main__':
    # Establish database conn
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    insert_notional_data(cursor)
    conn.commit()
    cursor.close()
    conn.close()
    cursor.close()