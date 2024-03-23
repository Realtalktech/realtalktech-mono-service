from rtt_data_app import create_app, db
from tests.databuilder import DataBuilder, DataInserter, UserFactory
from rtt_data_app.models import User, DiscussCategory, DiscoverVendor, UserDiscussCategory, Post, PostDiscussCategory, PostDiscoverVendor
from rtt_data_app.models import Comment, PostUpvote, CommentUpvote
from rtt_data_app.config import TestingConfig
import pytest
from unittest.mock import patch, MagicMock
from tests.commons import LoginResponse
import json

@pytest.fixture(scope='function')
def test_client():
    # Setup Flask app for testing
    app = create_app(config_class=TestingConfig)

    # Initialize testing DB
    with app.app_context():
        DataBuilder.init_test_database()
        DataInserter().init_test_database()
        # Create a test client for Flask application
        with app.test_client() as testing_client:
            yield testing_client

@pytest.fixture(autouse=True)
def bypass_token_required():
    """Fixture to bypass the token_required decorator."""
    with patch('rtt_data_app.auth.decorators.process_token', return_value = 1):
        yield

@pytest.fixture(scope='function')
def init_mock_feed():
    # Create categories, industries, interest areas, and vendors based on your lists
    categories = DiscussCategory.query.all()
    vendors = DiscoverVendor.query.all()

    # Create users
    user1 = User(username='user1', email='user1@example.com', full_name='User One', current_company='Company One', password='testpassword')
    user2 = User(username='user2', email='user2@example.com', full_name='User Two', current_company='Company Two', password='testpassword')
    subcats = []
    db.session.add_all([user1, user2])
    db.session.commit()

    # User subscriptions
    for category in [categories[0], categories[1]]:  # AI, Engineering
        user1_discussion = UserDiscussCategory(user_id=user1.id, category_id=category.id)
        db.session.add(user1_discussion)
        subcats.append(user1_discussion)


    for category in [categories[2], categories[3]]:  # Operations, Marketing
        user2_discussion = UserDiscussCategory(user_id=user2.id, category_id=category.id)
        db.session.add(user2_discussion)
        subcats.append(user2_discussion)


    db.session.commit()

    # Create posts and link them to categories and vendors
    mock_comment = Comment(post_id=1, user_id=1, comment_text="")
    posts = [
        Post(title="AI Post", body="This is a post about AI", user_id=user1.id, is_anonymous=False, comments=[mock_comment]),
        Post(title="Engineering and Operations Post", body="This is a post about Engineering and Operations", user_id=user2.id, is_anonymous=False, comments=[mock_comment]),
        Post(title="Marketing Post", body="This is a post about Marketing", user_id=user1.id, is_anonymous=True, comments=[mock_comment])
    ]
    db.session.add_all(posts)
    db.session.commit()

    associations = [
        PostDiscussCategory(post_id = posts[0].id, category_id=categories[0].id),
        PostDiscussCategory(post_id = posts[1].id, category_id=categories[1].id),
        PostDiscussCategory(post_id = posts[1].id, category_id=categories[2].id),
        PostDiscussCategory(post_id = posts[2].id, category_id=categories[3].id),
        PostDiscoverVendor(post_id = posts[0].id, vendor_id=vendors[0].id),
        PostDiscoverVendor(post_id = posts[1].id, vendor_id=vendors[2].id),
        PostDiscoverVendor(post_id = posts[2].id, vendor_id=vendors[3].id)
    ]
    db.session.add_all(associations)
    db.session.commit()

    # Create comments and upvotes for posts
    comments = [
        Comment(post_id=posts[0].id, user_id=user2.id, comment_text="Great post on AI!"),
        Comment(post_id=posts[1].id, user_id=user1.id, comment_text="Very informative on Engineering and Operations."),
    ]
    db.session.add_all(comments)
    db.session.commit()

    upvotes = [
        PostUpvote(post_id=posts[0].id, user_id=user2.id, is_downvote=False),
        PostUpvote(post_id=posts[1].id, user_id=user1.id, is_downvote=False),
        CommentUpvote(comment=comments[0], user_id=user1.id, is_downvote=False),
        CommentUpvote(comment=comments[1], user_id=user2.id, is_downvote=False),
    ]
    db.session.add_all(upvotes)
    db.session.commit()

    yield

    db.session.delete(upvotes[2])
    db.session.delete(upvotes[3])
    db.session.delete(comments[0])
    db.session.delete(comments[1])
    db.session.delete(upvotes[0])
    db.session.delete(upvotes[1])
    # for thing in associations: db.session.delete(thing)
    db.session.delete(posts[0])
    db.session.delete(posts[1])
    db.session.delete(posts[2])
    for thing in subcats: db.session.delete(thing)
    db.session.delete(user1)
    db.session.delete(user2)
    db.session.commit()


def test_get_feed_multiple_categories(test_client, init_mock_feed):
    # This test assumes the user is subscribed to multiple categories
    response = test_client.get('/feed', headers={'Authorization': 'Bearer valid-token-user1'})
    data = response.get_json()

    print(json.dumps(data,indent=2))

    assert response.status_code == 200
    assert len(data['posts']) >= 2  # User1 is subscribed to AI and Engineering
    # Ensure posts contain correct category names
    for post in data['posts']:
        assert 'categories' in post
        assert any(c in ["AI", "Engineering"] for c in post['categories'])

def test_get_feed_cross_listed_posts(test_client, init_mock_feed):
    # This test checks for cross-listed posts appearing in multiple categories
    response = test_client.get('/feed', headers={'Authorization': 'Bearer valid-token-user2'})
    data = response.get_json()

    assert response.status_code == 200
    assert len(data['posts']) >= 2  # User2 is subscribed to Operations and Marketing
    # Ensure there is a cross-listed post
    cross_listed_posts = [post for post in data['posts'] if len(post['categories']) > 1]
    assert len(cross_listed_posts) > 0

def test_user_interactions_reflected(test_client, init_mock_feed):
    # Check if user interactions like comments and upvotes are reflected
    response = test_client.get('/feed', headers={'Authorization': 'Bearer valid-token-user1'})
    data = response.get_json()

    assert response.status_code == 200
    # Check for reflected interactions
    for post in data['posts']:
        if 'num_upvotes' in post and post['num_upvotes'] > 0:
            assert post['num_comments'] > 0  # Ensure comments are also reflected
            break
