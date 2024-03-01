import json
from werkzeug.security import generate_password_hash
from unittest.mock import patch
from rtt_data_app.app import app, create_app, db
from rtt_data_app.models import User
from tests.databuilder import Databuilder, DataInserter
from config import TestingConfig
import pytest
from unittest.mock import patch

from tests.commons import MockInputs, VendorResponse

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

def test_get_discover_groups_success(test_client):
    response = test_client.get('/discover/groups', headers=MockInputs.MOCK_HEADER)
    data = response.get_json()
    print(json.dumps(data))
    assert response.status_code == 200
    assert data == VendorResponse.DISCOVER_GROUPS_RESPONSE

def test_get_discover_vendors_in_group_success(test_client):
    response = test_client.get('/group/1', headers=MockInputs.MOCK_HEADER)
    data = response.get_json()
    print(json.dumps(data))
    assert data == VendorResponse.CATEGORY_ONE_RESPONSE
    assert response.status_code == 200

def test_get_discover_vendors_in_group_fail_nonexistent_group(test_client):
    response = test_client.get('/group/99', headers=MockInputs.MOCK_HEADER)
    data = response.get_json()
    print(json.dumps(data))
    assert data == {"error": "Not Found Error", "message": "404 Not Found: Discover group not found"}
    assert response.status_code == 404

def test_get_vendor_page_success(test_client):
    response = test_client.get('/vendors/1', headers=MockInputs.MOCK_HEADER)
    data = response.get_json()
    print(json.dumps(data))
    assert data == VendorResponse.VENDOR_ONE_RESPONSE
    assert response.status_code == 200

def test_get_vendor_page_fail_nonexistent_vendor(test_client):
    response = test_client.get('/vendors/99', headers=MockInputs.MOCK_HEADER)
    data = response.get_json()
    print(json.dumps(data))
    assert data == {"error": "Not Found Error", "message": "404 Not Found: Vendor not found"}
    assert response.status_code == 404