from flask import Flask, jsonify, request
import pymysql
from flask import Flask
from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# Database connection details
HOST = 'rttdbstore-mydbinstance-msavqjqavkev.cnqm62ueodz0.us-east-1.rds.amazonaws.com'
USER = 'dbmaster'
PASSWORD = 'masterUser123!'
DB = 'RttAppDB'

def get_db_connection():
    return pymysql.connect(host=HOST,
                           user=USER,
                           password=PASSWORD,
                           db=DB,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/getComments', methods=['GET'])
def get_comments():
    post_id = request.args.get('postId', type=str)
    page = request.args.get('page', default=0, type=int)
    count = request.args.get('count', default=10, type=int)

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # SQL query to fetch comments
            sql = """
            SELECT Comment.*, User.username FROM Comment 
            JOIN User ON Comment.userId = User.id 
            WHERE Comment.postId = %s 
            LIMIT %s, %s;
            """
            cursor.execute(sql, (post_id, page * count, count))
            comments = cursor.fetchall()
    finally:
        connection.close()

    return jsonify(comments)

@app.route('/getPostsWithCommentIdsAndUpvotes', methods=['GET'])
def get_posts_with_comments_upvotes():
    category = request.args.get('category', type=str)
    page = request.args.get('page', default=0, type=int)
    count = request.args.get('count', default=10, type=int)

    posts_with_details = []

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Fetch posts with pagination
            sql = """
            SELECT Post.*, User.username FROM Post
            JOIN User ON Post.userId = User.id 
            WHERE Post.categoryId = (SELECT id FROM Category WHERE name = %s)
            LIMIT %s, %s;
            """
            cursor.execute(sql, (category, page * count, count))
            posts = cursor.fetchall()

            # For each post, fetch comment IDs and count upvotes
            for post in posts:
                cursor.execute("SELECT id FROM Comment WHERE postId = %s", (post['id'],))
                comments = cursor.fetchall()
                post['commentIds'] = [comment['id'] for comment in comments]

                cursor.execute("SELECT COUNT(*) AS upVotes FROM PostUpvote WHERE postId = %s", (post['id'],))
                upvotes = cursor.fetchone()
                post['upVotes'] = upvotes['upVotes']

                posts_with_details.append(post)

    finally:
        connection.close()

    return jsonify(posts_with_details)


if __name__ == '__main__':
    app.run(debug=True)
