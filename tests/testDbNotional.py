import os
import sys
# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from flask_testing import TestCase
import unittest


class TestFlaskApi(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def setUp(self):
        # Setup that runs before every test
        pass

    def tearDown(self):
        # Cleanup that runs after every test
        pass

    def test_get_comments(self):
        # Assuming valid postId from your notional data
        valid_postId = 1
        response = self.client.get(f'/getComments?postId={valid_postId}&page=0&count=10')
        self.assertEqual(response.status_code, 200)
        # Additional assertions based on the expected response

    def test_get_posts_with_comments_and_upvotes(self):
        # Assuming valid category name from your notional data
        valid_category = 'Home'
        response = self.client.get(f'/getPostsWithCommentIdsAndUpvotes?category={valid_category}&page=0&count=10')
        self.assertEqual(response.status_code, 200)
        # Additional assertions based on the expected response

# Run the tests
if __name__ == '__main__':
    unittest.main()
