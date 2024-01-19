import pymysql
import uuid
import random

# Database connection details
HOST = 'rttdbstore-mydbinstance-msavqjqavkev.cnqm62ueodz0.us-east-1.rds.amazonaws.com'
USER = 'dbmaster'
PASSWORD = 'masterUser123!'
DB = 'RttAppDB'

# Connect to the database
connection = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             db=DB,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        # Insert Users
        users = []
        for i in range(1, 11):
            user_id = str(uuid.uuid4())
            users.append(user_id)
            username = f'user{i}'
            password = f'password{i}'
            cursor.execute("INSERT INTO User (id, username, password) VALUES (%s, %s, %s)",
                           (user_id, username, password))
        
        # Insert Categories
        categories = ['Home', 'AI', 'Engineering', 'Operations', 'Marketing', 'Sales']
        for i, category in enumerate(categories):
            cursor.execute("INSERT INTO Category (id, name) VALUES (%s, %s)", (i, category))
        
        # Insert Posts and keep track of their IDs
        posts = []
        for i in range(1, 21):
            post_id = str(uuid.uuid4())
            posts.append(post_id)
            user_id = random.choice(users)  # Random user ID
            category_id = i % len(categories)  # Cyclically assign category
            title = f'Post Title {i}'
            description = f'Post Description {i}'
            cursor.execute("INSERT INTO Post (id, userId, categoryId, title, description) VALUES (%s, %s, %s, %s, %s)",
                           (post_id, user_id, category_id, title, description))
        
        # Insert Comments and keep track of their IDs
        comments = []
        for i in range(1, 31):
            comment_id = str(uuid.uuid4())
            comments.append(comment_id)
            user_id = random.choice(users)
            post_id = random.choice(posts)
            text = f'Comment text {i}'
            cursor.execute("INSERT INTO Comment (id, userId, postId, text) VALUES (%s, %s, %s, %s)",
                           (comment_id, user_id, post_id, text))

        # Insert CommentTags
        for i in range(1, 21):
            comment_id = random.choice(comments)
            tagged_user_id = random.choice(users)
            cursor.execute("INSERT INTO CommentTag (id, commentId, taggedUserId) VALUES (%s, %s, %s)",
                           (str(uuid.uuid4()), comment_id, tagged_user_id))

        # Insert CommentUpvotes
        for i in range(1, 31):
            comment_id = random.choice(comments)
            user_id = random.choice(users)
            cursor.execute("INSERT INTO CommentUpvote (id, commentId, userId) VALUES (%s, %s, %s)",
                           (str(uuid.uuid4()), comment_id, user_id))

        # Insert PostUpvotes
        for i in range(1, 31):
            post_id = random.choice(posts)
            user_id = random.choice(users)
            cursor.execute("INSERT INTO PostUpvote (id, userId, postId) VALUES (%s, %s, %s)",
                           (str(uuid.uuid4()), user_id, post_id))

    # Commit changes
    connection.commit()

finally:
    connection.close()

print("Database populated with notional data.")