import json
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import BadRequest
from unittest.mock import patch
from rtt_data_app.app import app, create_app, db
from rtt_data_app.models import User, Comment, CommentUpvote
from tests.databuilder import DataBuilder, DataInserter
from rtt_data_app.config import TestingConfig
import pytest
from unittest.mock import patch

from tests.commons import MockInputs, CommentResponse


@pytest.fixture(scope='module', autouse=True)
def test_client():
    """Fixture to set up Flask app for testing"""
    # Setup Flask app for testing
    app = create_app(config_class=TestingConfig)

    # Initialize testing DB
    with app.app_context():
        DataBuilder.init_test_database()
        DataInserter().init_test_database()
        DataInserter().init_sample_posts()
        # Create a test client for Flask application
        with app.test_client() as testing_client:
            yield testing_client

@pytest.fixture(scope='function', autouse=True)
def authorize_as_new_user():
    """Fixture to create a new user and make requests on their behalf."""
    user = User(username='testuser', 
                email='test@example.com', 
                full_name='Test User',
                current_company='Test Labs',
                password=generate_password_hash('password'))
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    token_return_value = user.id
    with patch('rtt_data_app.auth.decorators.process_token', return_value = token_return_value):
        yield user
    db.session.delete(user)
    db.session.commit()

def test_get_comments_for_post_success(test_client):
    request = {
        'postId': 1
    }
    response = test_client.get(
        '/getCommentsForPost',
        json=request,
        headers=MockInputs.MOCK_HEADER
    )
    data = response.get_json()
    print(json.dumps(data))
    for comment in data['comments']:
        comment.pop('updateTime')
        comment.pop('creationTime')

    assert data == CommentResponse.POST_ONE_COMMENTS_RESPONSE

    assert response.status_code == 200

def test_get_comments_for_post_fail_missing_id(test_client):
    request = {}
    response = test_client.get(
        '/getCommentsForPost',
        json=request,
        headers=MockInputs.MOCK_HEADER
    )
    data = response.get_json()

    print(json.dumps(data))
    assert data == {"error": "Bad request", "message": "400 Bad Request: postId is required"}

    assert response.status_code == BadRequest.code

def test_get_comments_for_post_fail_nonexistent_post(test_client):
    request = {
        'postId': 999
    }
    response = test_client.get(
        '/getCommentsForPost',
        json=request,
        headers=MockInputs.MOCK_HEADER
    )
    data = response.get_json()

    print(json.dumps(data))
    assert data == {"error": "Bad request", "message": "400 Bad Request: post does not exist!"}

    assert response.status_code == BadRequest.code

def test_create_comment_success(test_client, authorize_as_new_user):
    """
    Test making a comment on a post.
    """
    user = authorize_as_new_user  # Your function to authorize or create and login a user

    response = test_client.post(
        '/makeComment',
        json={
            'postId': 1,
            'commentText': 'This is a great post!',
            'taggedUsernames': ['elongates']
        },
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == "Comment added successfully"
    assert 'comment_id' in data

def test_create_comment_fail_missing_post_id(test_client):
    """
    Test making a comment on a post.
    """
    response = test_client.post(
        '/makeComment',
        json={
            'commentText': 'This is a great post!',
            'taggedUsernames': ['elongates']
        },
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == BadRequest.code
    data = response.get_json()
    assert data['message'] == "400 Bad Request: Missing required information to create comment"

def test_create_comment_fail_missing_comment_text(test_client):
    """
    Test making a comment on a post.
    """
    response = test_client.post(
        '/makeComment',
        json={
            'postId': 1,
            'taggedUsernames': ['elongates']
        },
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == BadRequest.code
    data = response.get_json()
    assert data['message'] == "400 Bad Request: Missing required information to create comment"

def test_vote_comment_success(test_client, authorize_as_new_user):
    user = authorize_as_new_user  # Your function to authorize or create and login a user
    comment = Comment(user_id=user.id, post_id=1, comment_text="Mock Comment")  # Create a comment as needed
    db.session.add(comment)
    db.session.commit()

    # Test upvoting a comment
    response = test_client.put(
        '/upvoteComment',
        json={
            'commentId': comment.id,
            'isDownvote': False
        },
        headers={"Authorization": "Bearer valid-token"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == "Vote updated successfully"

    # Verify that the vote was added to the database
    vote = CommentUpvote.query.filter_by(comment_id=comment.id, user_id=user.id).first()
    assert vote is not None
    assert vote.is_downvote == False

    # Test changing the vote to none
    response = test_client.put(
        '/upvoteComment',
        json={
            'commentId': comment.id,
            'isDownvote': True
        },
        headers={"Authorization": "Bearer valid-token"}
    )
    assert response.status_code == 200

    # Verify that the vote was updated in the database
    vote = CommentUpvote.query.filter_by(comment_id=comment.id, user_id=user.id).first()
    assert vote is None

    # Test changing the vote to downvote
    response = test_client.put(
        '/upvoteComment',
        json={
            'commentId': comment.id,
            'isDownvote': True
        },
        headers={"Authorization": "Bearer valid-token"}
    )
    assert response.status_code == 200
    vote:CommentUpvote = CommentUpvote.query.filter_by(comment_id=comment.id, user_id=user.id).first()
    assert vote is not None
    assert vote.is_downvote == True

    # Clean up after test
    db.session.delete(vote)
    db.session.delete(comment)
    db.session.commit()

def test_vote_comment_fail_missing_comment_id(test_client, authorize_as_new_user):
    user = authorize_as_new_user  # Your function to authorize or create and login a user
    comment = Comment(user_id=user.id, post_id=1, comment_text="Mock Comment")  # Create a comment as needed
    db.session.add(comment)
    db.session.commit()

    # Test upvoting a comment
    response = test_client.put(
        '/upvoteComment',
        json={
            'isDownvote': False
        },
        headers={"Authorization": "Bearer valid-token"}
    )
    assert response.status_code == 400
    data = response.get_json()
    print(data)
    assert data == {'error': 'Bad request', 'message': '400 Bad Request: Comment ID is required'}

    # Clean up after test
    db.session.delete(comment)
    db.session.commit()

def test_vote_comment_fail_missing_vote_intention(test_client, authorize_as_new_user):
    user = authorize_as_new_user  # Your function to authorize or create and login a user
    comment = Comment(user_id=user.id, post_id=1, comment_text="Mock Comment")  # Create a comment as needed
    db.session.add(comment)
    db.session.commit()

    # Test upvoting a comment
    response = test_client.put(
        '/upvoteComment',
        json={
            'commentId' : 1
        },
        headers={"Authorization": "Bearer valid-token"}
    )
    assert response.status_code == 400
    data = response.get_json()
    print(data)
    assert data == {'error': 'Bad request', 'message': "400 Bad Request: Vote intention is required"}

    # Clean up after test
    db.session.delete(comment)
    db.session.commit()

