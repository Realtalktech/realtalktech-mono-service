"""This file is ONLY to be used with non-PROD Databases."""

import os
import sys
# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from flask_testing import TestCase
import pytest
from app import create_app
import pymysql
import pymysql.cursors
import time
import json

# Database connection details
HOST="realtalktechrdsstack-realtalktechdbinstance-c7ciisdczocf.cnqm62ueodz0.us-east-1.rds.amazonaws.com"
USER="admin"
PASSWORD="ReallyRealAboutTech123!"
DB = "RealTalkTechDB"

def get_db_connection():
    return pymysql.connect(host=HOST,
                           user=USER,
                           password=PASSWORD,
                           db=DB,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

@pytest.fixture(scope="module")
def setup_and_teardown_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("Inserting test data...")

    user_id, category_ids, category_names, post_ids = insert_test_data(cursor)

    conn.commit()
    print("Test data inserted.")

    yield user_id, category_ids, category_names, post_ids

    print("Cleaning up test data...")

    delete_test_data(cursor)

    conn.commit()
    cursor.close()
    conn.close()
    print("Test data cleaned up.")

def insert_test_data(cursor):
    """This will eventually be removed in lieu of calls to upcoming @POST methods."""
    # Insert a test user
    cursor.execute("INSERT INTO User (first_name, last_name, username, email, password) VALUES ('Test', 'User', 'test_user', 'test@example.com', 'password')")
    cursor.execute("SELECT LAST_INSERT_ID()")
    user_id = cursor.fetchone()['LAST_INSERT_ID()']

    # Insert test categories
    category_names = ['test1', 'test2', 'test3', 'test4']
    category_ids = []
    for name in category_names:
        cursor.execute("INSERT INTO Category (category_name) VALUES (%s)", (name,))
        cursor.execute("SELECT LAST_INSERT_ID()")
        category_id = cursor.fetchone()['LAST_INSERT_ID()']
        category_ids.append(category_id)
        
        if(name == 'test1' or name == 'test2'):
            # Associate user with the category
            cursor.execute("INSERT INTO UserCategory (user_id, category_id) VALUES (%s, %s)", (user_id, category_id))

    # Insert mock posts in each category
    post_ids = []
    postNum = 1
    for category_id in category_ids:
        for i in range(20):  # 20 posts per category
            cursor.execute("INSERT INTO Post (user_id, title, body) VALUES (%s, 'Mock title %s', 'Mock body %s')", (user_id, postNum, postNum))
            cursor.execute("SELECT LAST_INSERT_ID()")
            post_id = cursor.fetchone()['LAST_INSERT_ID()']
            post_ids.append(post_id)

            # Link post to category
            cursor.execute("INSERT INTO PostCategory (post_id, category_id) VALUES (%s, %s)", (post_id, category_id))
            postNum = postNum + 1

    # Insert 20 mock comments into the first post
    commentPost = post_ids[0]
    for i in range(20):
        cursor.execute("INSERT INTO Comment (post_id, user_id, comment_text) VALUES (%s, %s, 'Mock Comment %s')", (commentPost, user_id, i + 1))

    return user_id, category_ids, category_names, post_ids

def delete_test_data(cursor):
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("TRUNCATE TABLE User")
    cursor.execute("TRUNCATE TABLE Post")
    cursor.execute("TRUNCATE TABLE Category")
    cursor.execute("TRUNCATE TABLE UserCategory")
    cursor.execute("TRUNCATE TABLE PostCategory")
    cursor.execute("TRUNCATE TABLE Vendor")
    cursor.execute("TRUNCATE TABLE UserVendor")
    cursor.execute("TRUNCATE TABLE PostVendor")
    cursor.execute("TRUNCATE TABLE Comment")
    cursor.execute("TRUNCATE TABLE CommentTag")
    cursor.execute("TRUNCATE TABLE PostUpvote")
    cursor.execute("TRUNCATE TABLE CommentUpvote")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

@pytest.fixture
def client():
    flask_app = create_app()
    with flask_app.test_client() as client:
        yield client

class TestAPI:
    def test_get_feed(self, client, setup_and_teardown_db):
        """Testing correct retrieval of posts in category 4"""
        user_id, category_ids, category_names, post_ids = setup_and_teardown_db

        print("Testing get_feed endpoint...")

        response1 = client.get('/feed', query_string={'categoryId': category_ids[3], 'page': 1, 'count': 10})
        posts_page_1 = response1.get_json()

        response2 = client.get('/feed', query_string={'categoryId': category_ids[3], 'page': 2, 'count': 10})
        posts_page_2 = response2.get_json()

        print("Response for page 1:", posts_page_1)
        print("Response for page 2:", posts_page_2)

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert len(posts_page_1) == 10
        assert len(posts_page_2) == 10

        expected_post_ids_page_1 = post_ids[-1:-11:-1]  # Last 10 post IDs
        expected_post_ids_page_2 = post_ids[-11:-21:-1]  # Previous 10 post IDs

        for i, post in enumerate(posts_page_1):
            assert post['id'] == expected_post_ids_page_1[i]
            assert post['title'] == f'Mock title {80 - i}'
            assert post['body'] == f'Mock body {80 - i}'
            assert 'creation_time' in post  # Check if creation_time is present
            assert isinstance(post['id'], int)  # Check if post_id is an integer
            assert isinstance(post['body'], str)  # Check if body is a string


        for i, post in enumerate(posts_page_2):
            assert post['id'] == expected_post_ids_page_2[i]
            assert post['title'] == f'Mock title {70 - i}'
            assert post['body'] == f'Mock body {70 - i}'
            assert 'creation_time' in post  # Check if creation_time is present
            assert isinstance(post['id'], int)  # Check if post_id is an integer
            assert isinstance(post['body'], str)  # Check if body is a string


        print("Test completed.")

    def test_get_feed_all_category(self, client, setup_and_teardown_db):
            """Assuming user is interested in categories 1 and 2"""
            user_id, category_ids, category_names, post_ids = setup_and_teardown_db

            print("Testing get_feed endpoint for All category...")

            response_page_1 = client.get('/feed', query_string={'userId': user_id, 'page': 1, 'count': 20})
            response_page_2 = client.get('/feed', query_string={'userId': user_id, 'page': 2, 'count': 20})
            posts_page_1 = response_page_1.get_json()
            posts_page_2 = response_page_2.get_json()
            json_formatted_str_page_1 = json.dumps(posts_page_1, indent = 2)
            json_formatted_str_page_2 = json.dumps(posts_page_2, indent = 2)
            print("Response for All category Page 1:\n",json_formatted_str_page_1)
            print("Response for All category Page 2:\n",json_formatted_str_page_2)

            assert response_page_1.status_code == 200
            assert response_page_2.status_code == 200
            assert len(posts_page_1) <= 20

            # Assert that posts are from the categories the user is interested in
            for post in posts_page_1:
                print("WHAT THE HELL BRUH: ", type(post['categories']))
                assert post['categories'][0] == "test2"
            for post in posts_page_2:
                assert post['categories'][0] == "test1"

            print("Test for get_feed All category completed.")

    def test_get_comments(self, client, setup_and_teardown_db):
        user_id, category_ids, category_names, post_ids = setup_and_teardown_db

        print("Testing get_comments endpoint...")

        response1 = client.get('/getComments', query_string={'postId': post_ids[0], 'page': 1, 'count': 10})
        comments_page_1 = response1.get_json()

        response2 = client.get('/getComments', query_string={'postId': post_ids[0], 'page': 2, 'count': 10})
        comments_page_2 = response2.get_json()

        print("Response for page 1:", json.dumps(comments_page_1, indent = 2))
        print("Response for page 2:", json.dumps(comments_page_2, indent = 2))

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert len(comments_page_1) == 10
        assert len(comments_page_2) == 10

        # Assertions for the first page of comments
        for i, comment in enumerate(comments_page_1):
            assert comment['user_id'] == user_id  # Check if the user_id matches
            assert f"Mock Comment {20 - i}" in comment['comment_text']  # Check the presence of comment text
            assert 'creation_time' in comment  # Check if creation_time is present
            assert isinstance(comment['id'], int)  # Check if comment_id is an integer
            assert isinstance(comment['comment_text'], str)  # Check if comment_text is a string

        # Assertions for the second page of comments
        for i, comment in enumerate(comments_page_2):
            assert comment['user_id'] == user_id
            assert f"Mock Comment {10 - i}"  in comment['comment_text']
            assert 'creation_time' in comment
            assert isinstance(comment['id'], int)
            assert isinstance(comment['comment_text'], str)

        print("Test for get_comments completed.")

def main():
    pytest.main()

if __name__ == '__main__':
    main()