import pymysql

# Database connection details
HOST = 'rttdbstore-mydbinstance-msavqjqavkev.cnqm62ueodz0.us-east-1.rds.amazonaws.com'
USER = 'dbmaster'
PASSWORD = 'masterUser123!'
DB = 'RttAppDB'

connection = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        # List of tables to clear, modify as needed
        tables = ['CommentUpvote', 'PostUpvote', 'CommentTag', 'Comment', 'Post', 'User', 'Category']
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")
    connection.commit()
finally:
    connection.close()

print("Database cleared.")
