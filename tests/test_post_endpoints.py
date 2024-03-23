from functools import wraps
from unittest.mock import patch
from rtt_data_app.app import app, create_app, db
from rtt_data_app.models import Post, PostUpvote
from tests.databuilder import DataBuilder, DataInserter
from rtt_data_app.config import TestingConfig
from functools import wraps
import pytest
from unittest.mock import patch

from tests.commons import MockInputs, PostResponse

responder = PostResponse()

@pytest.fixture(scope='session')
def test_client():
    """Fixture to set up Flask app for testing"""
    # Setup Flask app for testing
    app = create_app(config_class=TestingConfig)

    # Initialize testing DB
    with app.app_context():
        DataBuilder.init_test_database()
        inserter = DataInserter()
        # Create a test client for Flask application
        with app.test_client() as testing_client:
            yield testing_client

# Automatically bypasses token check as user #1 (elongates)
@pytest.fixture(autouse=True)
def bypass_token_required():
    """Fixture to bypass the token_required decorator."""
    with patch('rtt_data_app.auth.decorators.process_token', return_value = 1):
        yield

def test_create_public_post_success(test_client):
    post_data = {
        'title': 'Mock Post 1',
        'body': 'Mock Body 1',
        'categories': [1,2,3],
        'isAnonymous': False,
        'vendors': [1,2,3]
    }
    response = test_client.post('/makePost', json=post_data, headers=MockInputs.MOCK_HEADER)
    print(response)
    response_data = response.get_json()
    print(response_data)
    assert response_data == responder.create_post_response()
    assert response.status_code == 201

def test_create_anonymous_post_sucess(test_client):
    post_data = {
        'title': 'Mock Post 1',
        'body': 'Mock Body 1',
        'categories': [1,2,3],
        'isAnonymous': True,
        'vendors': [1,2,3]
    }
    response = test_client.post('/makePost', json=post_data, headers=MockInputs.MOCK_HEADER)
    print(response)
    response_data = response.get_json()
    print(response_data)
    assert response_data == responder.create_post_response()
    assert response.status_code == 201

def test_create_post_fail_missing_title(test_client):
    post_data = {
        'body': 'Mock Body 1',
        'categories': [1,2,3],
        'isAnonymous': True,
        'vendors': [1,2,3]
    }
    response = test_client.post('/makePost', json=post_data, headers=MockInputs.MOCK_HEADER)
    response_data = response.get_json()
    assert response_data == responder.missing_fields_response_builder(title=True)
    assert response.status_code == 400 # Bad Request

def test_create_post_fail_missing_body(test_client):
    post_data = {
        'title': 'Mock Title 1',
        'categories': [1,2,3],
        'isAnonymous': True,
        'vendors': [1,2,3]
    }
    response = test_client.post('/makePost', json=post_data, headers=MockInputs.MOCK_HEADER)
    response_data = response.get_json()
    assert response_data == responder.missing_fields_response_builder(body=True)
    assert response.status_code == 400 # Bad Request

def test_create_post_fail_missing_anonymity_status(test_client):
    post_data = {
        'title': 'Mock Title 1',
        'body': 'Mock Body 1',
        'categories': [1,2,3],
        'vendors': [1,2,3]
    }
    response = test_client.post('/makePost', json=post_data, headers=MockInputs.MOCK_HEADER)
    response_data = response.get_json()
    assert response_data == responder.missing_fields_response_builder(is_anonymous=True)
    assert response.status_code == 400 # Bad Request

def test_edit_post_success(test_client):
    # Setup - retrieve post_id from first test case
    post_id = responder.EXPECTED_POST_ID - 1

    # The IDs of existing categories and vendors for the post
        # original_category_ids = [1,2,3] 
        # original_vendor_ids = [1,2,3] 

    # IDs for new categories and vendors
    new_category_ids = [4, 5, 6]  # Change categories
    new_vendor_ids = [4, 5, 6]  # Change vendors

    post_data = {
        'postId' : post_id,
        'title': 'New Title',
        'body': 'New Body',
        'categories': new_category_ids,
        'vendors': new_vendor_ids
    }

    # Execute
    response = test_client.put('/editPost', json=post_data, headers=MockInputs.MOCK_HEADER)
    response_data = response.get_json()
    assert response.status_code == 200
    assert response_data == responder.edit_post_response()

    # Verify
    updated_post = Post.query.get(post_id)
    assert updated_post.title == 'New Title'
    assert updated_post.body == 'New Body'
    assert sorted([cat.id for cat in updated_post.categories]) == sorted(new_category_ids)
    assert sorted([ven.id for ven in updated_post.vendors]) == sorted(new_vendor_ids)

def test_edit_post_fail_nonexistent_post(test_client):
    post_data = {
        'postId': 10000
    }
    # Execute
    response = test_client.put('/editPost', json=post_data, headers=MockInputs.MOCK_HEADER)
    response_data = response.get_json()
    print(response_data)
    assert response.status_code == 400
    assert response_data == PostResponse.EDIT_UNOWNED_POST_RESPONSE

def test_edit_post_fail_unowned_post(test_client):
    post_data = {
        'postId': 5
    }
    # Execute
    response = test_client.put('/editPost', json=post_data, headers=MockInputs.MOCK_HEADER)
    response_data = response.get_json()
    print(response_data)
    assert response.status_code == 400
    assert response_data == PostResponse.EDIT_UNOWNED_POST_RESPONSE

def test_edit_post_fail_missing_post_id(test_client):
    post_data = {}
    # Execute
    response = test_client.put('/editPost', json=post_data, headers=MockInputs.MOCK_HEADER)
    response_data = response.get_json()
    print(response_data)
    assert response.status_code == 400
    assert response_data == PostResponse.MISSING_POST_ID_RESPONSE

def test_insert_new_upvote_success(test_client):
    post = Post(title='TestPost', body='Test Body', is_anonymous=False, user_id=1)
    db.session.add(post)
    db.session.commit()

    vote_data = {
        'postId': post.id,
        'isDownvote': False
    }

    response = test_client.put('/upvotePost', json=vote_data, headers=MockInputs.MOCK_HEADER)
    response_data = response.get_json()

    assert response.status_code == 200
    assert response_data == PostResponse.VOTE_POST_SUCCESS_RESPONSE

    updated_vote = PostUpvote.query.filter_by(post_id=post.id, user_id=1).first()
    assert updated_vote is not None
    assert updated_vote.is_downvote is False

def test_insert_new_downvote_success(test_client):
    post = Post(title='TestPost', body='Test Body', is_anonymous=False, user_id=1)
    db.session.add(post)
    db.session.commit()

    vote_data = {
        'postId': post.id,
        'isDownvote': True
    }

    response = test_client.put('/upvotePost', json=vote_data, headers=MockInputs.MOCK_HEADER)
    response_data = response.get_json()

    assert response.status_code == 200
    assert response_data == PostResponse.VOTE_POST_SUCCESS_RESPONSE

    updated_vote = PostUpvote.query.filter_by(post_id=post.id, user_id=1).first()
    assert updated_vote is not None
    assert updated_vote.is_downvote is True

def test_toggle_upvote_to_none_success(test_client):
    post = Post(title='TestPost', body='Test Body', is_anonymous=False, user_id=1)
    db.session.add(post)
    db.session.commit()

    # Initial upvote
    initial_vote = PostUpvote(post_id=post.id, user_id=1, is_downvote=False)
    db.session.add(initial_vote)
    db.session.commit()

    # Ensure the upvote was inserted
    assert PostUpvote.query.filter_by(post_id=post.id, is_downvote=False).count() == 1

    vote_data = {
        'postId': post.id,
        'isDownvote': True
    }

    response = test_client.put('/upvotePost', json=vote_data, headers=MockInputs.MOCK_HEADER)
    response_data = response.get_json()

    assert response.status_code == 200
    assert response_data == PostResponse.VOTE_POST_SUCCESS_RESPONSE

    updated_vote = PostUpvote.query.filter_by(post_id=post.id, user_id=1).first()
    assert updated_vote is None

def test_toggle_downvote_to_none_success(test_client):
    post = Post(title='TestPost', body='Test Body', is_anonymous=False, user_id=1)
    db.session.add(post)
    db.session.commit()

    # Initial downvote
    initial_vote = PostUpvote(post_id=post.id, user_id=1, is_downvote=True)
    db.session.add(initial_vote)
    db.session.commit()

    # Ensure the downvote was inserted
    assert PostUpvote.query.filter_by(post_id=post.id, is_downvote=True).count() == 1

    vote_data = {
        'postId': post.id,
        'isDownvote': False
    }

    response = test_client.put('/upvotePost', json=vote_data, headers=MockInputs.MOCK_HEADER)
    response_data = response.get_json()

    assert response.status_code == 200
    assert response_data == PostResponse.VOTE_POST_SUCCESS_RESPONSE

    updated_vote = PostUpvote.query.filter_by(post_id=post.id, user_id=1).first()
    assert updated_vote is None

def test_toggle_upvote_to_upvote_success(test_client):
    post = Post(title='TestPost', body='Test Body', is_anonymous=False, user_id=1)
    db.session.add(post)
    db.session.commit()

    # Initial upvote
    initial_vote = PostUpvote(post_id=post.id, user_id=1, is_downvote=False)
    db.session.add(initial_vote)
    db.session.commit()

    # Ensure the downvote was inserted
    assert PostUpvote.query.filter_by(post_id=post.id, is_downvote=False).count() == 1

    vote_data = {
        'postId': post.id,
        'isDownvote': False
    }

    response = test_client.put('/upvotePost', json=vote_data, headers=MockInputs.MOCK_HEADER)
    response_data = response.get_json()

    assert response.status_code == 200
    assert response_data == PostResponse.VOTE_POST_SUCCESS_RESPONSE

    updated_vote = PostUpvote.query.filter_by(post_id=post.id, user_id=1).first()
    assert updated_vote.is_downvote == False

def test_toggle_downvote_to_downvote_success(test_client):
    post = Post(title='TestPost', body='Test Body', is_anonymous=False, user_id=1)
    db.session.add(post)
    db.session.commit()

    # Initial downvote
    initial_vote = PostUpvote(post_id=post.id, user_id=1, is_downvote=True)
    db.session.add(initial_vote)
    db.session.commit()

    # Ensure the downvote was inserted
    assert PostUpvote.query.filter_by(post_id=post.id, is_downvote=True).count() == 1

    vote_data = {
        'postId': post.id,
        'isDownvote': True
    }

    response = test_client.put('/upvotePost', json=vote_data, headers=MockInputs.MOCK_HEADER)
    response_data = response.get_json()

    assert response.status_code == 200
    assert response_data == PostResponse.VOTE_POST_SUCCESS_RESPONSE

    updated_vote = PostUpvote.query.filter_by(post_id=post.id, user_id=1).first()
    assert updated_vote.is_downvote == True

def test_toggle_vote_fail_missing_post_id(test_client):
    vote_data = {
        'isDownvote': True
    }

    response = test_client.put('/upvotePost', json=vote_data, headers=MockInputs.MOCK_HEADER)
    response_data = response.get_json()

    assert response.status_code == 400 # Bad request
    assert response_data == PostResponse.VOTE_POST_FAIL_MISSING_ID

def test_toggle_vote_fail_missing_intention(test_client):
    vote_data = {
        'postId': 5
    }

    response = test_client.put('/upvotePost', json=vote_data, headers=MockInputs.MOCK_HEADER)
    response_data = response.get_json()

    assert response.status_code == 400 # Bad request
    assert response_data == PostResponse.VOTE_POST_FAIL_MISSING_INTENTION