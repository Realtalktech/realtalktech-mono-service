import pymysql
import uuid

# Database connection details
HOST = 'rttdbstore-mydbinstance-msavqjqavkev.cnqm62ueodz0.us-east-1.rds.amazonaws.com'
USER = 'dbmaster'
PASSWORD = 'masterUser123!'
DB = 'RttAppDB'

connection = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        # Insert Users
        users = [str(uuid.uuid4()) for _ in range(10)]
        for i, user_id in enumerate(users):
            username = f'user{i+1}'
            password = f'password{i+1}'
            cursor.execute("INSERT INTO User (id, username, password) VALUES (%s, %s, %s)", (user_id, username, password))
        
        # Insert Categories
        categories = ['Home', 'AI', 'Engineering', 'Operations', 'Marketing', 'Sales', 'Customer Success', 'Data', 'Product', 'HR & Talent', 'Finance', 'Leadership/Exec', 'Founder', 'Investor/VC']
        for i, category in enumerate(categories):
            cursor.execute("INSERT INTO Category (id, name) VALUES (%s, %s)", (i, category))

        # Each User Creates a Post in Each Category
        for user_id in users:
            for category_id in range(len(categories)):
                post_id = str(uuid.uuid4())
                title = f'Post by {user_id} in {categories[category_id]}'
                description = f'Description for post {title}'
                cursor.execute("INSERT INTO Post (id, userId, categoryId, title, description) VALUES (%s, %s, %s, %s, %s)", (post_id, user_id, category_id, title, description))

                # Each User Comments on Their Own Post
                comment_id = str(uuid.uuid4())
                text = f'Comment on post {title}'
                cursor.execute("INSERT INTO Comment (id, userId, postId, text) VALUES (%s, %s, %s, %s)", (comment_id, user_id, post_id, text))

                # Each User Upvotes Their Own Comment
                cursor.execute("INSERT INTO CommentUpvote (id, commentId, userId) VALUES (%s, %s, %s)", (str(uuid.uuid4()), comment_id, user_id))

    connection.commit()
finally:
    connection.close()

print("Database populated with notional data.")

