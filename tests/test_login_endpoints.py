from rtt_data_app import create_app, db
from tests.databuilder import Databuilder, DataInserter
from config import TestingConfig
import pytest
from unittest.mock import patch, MagicMock
from tests.commons import LoginResponse


mock_user = LoginResponse.MockUser()
@pytest.fixture(scope='session')
def test_client():
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
def generate_mock_token():
    with patch('rtt_data_app.auth.token_auth.Authorizer.generate_token', return_value={'MockToken': 'MockToken'}):
        yield

# @patch('app.auth.token_required', return_value=lambda x:x)
def test_signup_success(test_client, generate_mock_token):
    signup_data = mock_user.get_signup_data()
    response = test_client.put('/signup', json=signup_data)
    response_data = response.get_json()
    assert response_data == LoginResponse.SIGNUP_SUCCESS
    assert response.status_code == 201

def test_signup_failure_spammy_email(test_client):
    signup_data = mock_user.get_signup_data(success=False)
    signup_data['email'] = f"testuser{mock_user.id}@localhost.com"
    response = test_client.put('/signup', json=signup_data)
    response_data = response.get_json()
    assert response_data == LoginResponse.LOCALHOST_EMAIL_RESPONSE
    assert response.status_code == 400 # Bad request 

def test_signup_failure_missing_fullname(test_client):
    signup_data = mock_user.get_signup_data(success=False)
    signup_data['fullname'] = None
    response = test_client.put('/signup', json=signup_data)
    response_data = response.get_json()
    assert response_data == LoginResponse.missing_fields_builder(full_name=True)
    assert response.status_code == 400 # Bad request 

def test_signup_failure_missing_username(test_client):
    signup_data = mock_user.get_signup_data(success=False)
    signup_data['username'] = None
    response = test_client.put('/signup', json=signup_data)
    response_data = response.get_json()
    assert response_data == LoginResponse.missing_fields_builder(username=True)
    assert response.status_code == 400 # Bad request

def test_signup_failure_missing_password(test_client):
    signup_data = mock_user.get_signup_data(success=False)
    signup_data['password'] = None
    response = test_client.put('/signup', json=signup_data)
    response_data = response.get_json()
    assert response_data == LoginResponse.missing_fields_builder(password=True)
    assert response.status_code == 400 # Bad request

def test_signup_failure_missing_current_company(test_client):
    signup_data = mock_user.get_signup_data(success=False)
    signup_data['currentCompany'] = None
    response = test_client.put('/signup', json=signup_data)
    response_data = response.get_json()
    assert response_data == LoginResponse.missing_fields_builder(current_company=True)
    assert response.status_code == 400 # Bad request

def test_login_with_username_success(test_client, generate_mock_token):
        login_json = LoginResponse.ELON().login_creds
        login_response = test_client.post('/login', json=login_json)
        login_response_data = login_response.get_json()
        assert login_response.status_code == 200
        # Remove times for proper asserts
        login_response_data['userDetails'].pop('accountCreationTime', None)
        login_response_data['userDetails'].pop('accountUpdateTime', None)

        assert login_response_data == LoginResponse.ELON().login_response

def test_login_with_username_fail_wrong_password(test_client):
        login_json = LoginResponse.ELON().login_creds
        login_json['password'] = 'wrongpassword'
        login_response = test_client.post('/login', json=login_json)
        login_response_data = login_response.get_json()
        assert login_response.status_code == 401
        assert login_response_data == LoginResponse.INCORRECT_PASSWORD_RESPONSE

def test_login_with_username_fail_nonexistent_user(test_client):
    login_json = {
        'username': 'joebiden',
        'password': 'sleepy'
    }
    login_response = test_client.post('/login', json=login_json)
    assert login_response.status_code == 401
    assert login_response.data == b'{"error":"Unauthorized","message":"401 Unauthorized: Invalid Username"}\n'

def test_login_with_email_success(test_client, generate_mock_token):
    login_json = {
        'username': LoginResponse.ELON().email,
        'password': LoginResponse.ELON().password
    }
    login_response = test_client.post('/login', json=login_json)
    assert login_response.status_code == 200
    login_response_data = login_response.get_json()
    # Remove times for proper asserts
    login_response_data['userDetails'].pop('accountCreationTime', None)
    login_response_data['userDetails'].pop('accountUpdateTime', None)

    assert login_response_data == LoginResponse.ELON().login_response
        
def test_login_with_email_fail_wrong_password(test_client):
    login_json = {
        'username': LoginResponse.ELON().email,
        'password': LoginResponse.ELON().password+'1'
    }
    login_response = test_client.post('/login', json=login_json)
    login_response_data = login_response.get_json()
    assert login_response.status_code == 401
    assert login_response_data == LoginResponse.INCORRECT_PASSWORD_RESPONSE

def test_login_with_email_fail_nonexistent_user(test_client, generate_mock_token):
    login_json = {
        'username': 'joe@biden.com',
        'password': 'sleepysleepy'
    }
    
    login_response = test_client.post('/login', json=login_json)
    login_response_data = login_response.get_json()
    assert login_response.status_code == 401
    assert login_response_data == LoginResponse.INVALID_EMAIL_RESPONSE