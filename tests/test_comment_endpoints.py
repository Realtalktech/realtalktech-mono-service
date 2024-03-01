import json
from werkzeug.security import generate_password_hash
from unittest.mock import patch
from rtt_data_app.app import app, create_app, db
from rtt_data_app.models import User
from tests.databuilder import Databuilder, DataInserter
from config import TestingConfig
import pytest
from unittest.mock import patch

from tests.commons import MockInputs, CommentResponse

@pytest.fixture(scope='session')
def test_client():
    """Fixture to set up Flask app for testing"""
    # Setup Flask app for testing
    app = create_app(config_class=TestingConfig)

    # Initialize testing DB
    with app.app_context():
        Databuilder.init_test_database()
        inserter = DataInserter()
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
    for comment in data['comments']:
        comment.pop('updateTime')
        comment.pop('creationTime')

    print(json.dumps(data))
    
    
    assert data == CommentResponse.POST_ONE_COMMENTS_RESPONSE

    assert response.status_code == 200
    