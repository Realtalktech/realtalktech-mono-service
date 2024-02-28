from functools import wraps
from unittest.mock import patch

def mock_decorator():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    return decorator

patch('rtt_data_app.routes.post.token_required',mock_decorator).start()

from rtt_data_app.app import app, create_app, db
from tests.databuilder import Databuilder, DataInserter
from config import TestingConfig
from functools import wraps
import pytest
from unittest.mock import patch, MagicMock
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='module')
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

@pytest.fixture()
def bypass_token_required():
    """Fixture to bypass the token_required decorator."""
    # with patch('rtt_data_app.routes.post.token_required', lambda f:f):
    #     yield
    # with patch('rtt_data_app.routes.post.token_required') as mock_token_required:
    #     def token_required(f):
    #         @wraps(f)
    #         def decorated_function(*args, **kwargs):
    #             return f(1, *args, **kwargs)  # Assuming '1' is a valid user_id for testing
    #         return decorated_function
    #     mock_token_required.side_effect = token_required
    #     yield
    # original = rtt_data_app.routes.post.token_required
    # rtt_data_app.routes.post.token_required = lambda f: f  # Bypass decorator entirely
    # yield
    # rtt_data_app.routes.post.token_required = original  # Restore after test
    with patch('rtt_data_app.routes.post.token_required') as mock:
        def mock_decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                return f(1, *args, **kwargs)  # Assuming '1' is a valid user_id for testing purposes
            return decorated
        mock.side_effect = mock_decorator
        yield

def test_create_public_post_success(test_client):
    post_data = {
        'title': 'Mock Post 1',
        'body': 'Mock Body 1',
        'categories': [1,2,3],
        'isAnonymous': False,
        'vendors': [1,2,3]
    }
    # Simulate header
    headers = {
        'Authorization': 'Bearer_mock_token'
    }
    # Indicates post being made under user_id 1 (elongates)
    # with patch('rtt_data_app.routes.post.token_required', return_value=lambda f: lambda *args, **kwargs: f(1, *args, **kwargs)):
    response = test_client.post('/makePost', json=post_data)
    print(response)
    response_data = response.get_json()
    print(response_data)
    assert response_data == {"message": "Signup successful", "token": {"MockToken": "MockToken"}}
    assert response.status_code == 201