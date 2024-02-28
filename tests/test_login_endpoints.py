from rtt_data_app import create_app, db
from tests.databuilder import Databuilder, DataInserter
from config import TestingConfig
import pytest
from unittest.mock import patch, MagicMock
from tests.commons import LoginResponse

@pytest.fixture(scope='module')
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
    signup_data = {
        'fullname': 'Test User1',
        'username': 'testuser1',
        'email': 'testuser1@gmail.com',
        'password': 'password',
        'techstack': [1, 2, 3, 4, 5],
        'currentCompany': 'Test Labs',
        'industryInvolvement': [1, 2, 3, 4, 5],
        'workCategories': [1, 2, 3],
        'linkedinUrl': 'https://linkedin.com/testuser',
        'bio': 'I am a test user.',
        'interestAreas': [1, 2, 3]
    }
    response = test_client.put('/signup', json=signup_data)
    response_data = response.get_json()
    assert response_data == LoginResponse.SIGNUP_SUCCESS
    assert response.status_code == 201

def test_signup_failure_spammy_email(test_client):
    json = {
        'fullname': 'Test User1',
        'username': 'testuser1',
        'email': 'testuser1@localhost.com',
        'password': 'password',
        'techstack': [1,2,3,4,5],
        'currentCompany': 'Test Labs',
        'industryInvolvement': [1,2,3,4,5],
        'workCategories': [1,2,3],
        'linkedinUrl': 'https://linkedin.com/testuser',
        'bio': 'I am a test user.',
        'interestAreas': [1,2,3]
    }
    response = test_client.put('/signup', json=json)
    response_data = response.get_json()
    assert response_data == LoginResponse.LOCALHOST_EMAIL_RESPONSE
    assert response.status_code == 400 # Bad request 

def test_signup_failure_missing_fullname(test_client):
    json = {
        'username': 'testuser1',
        'email': 'testuser1@gmail.com',
        'password': 'password',
        'techstack': [1,2,3,4,5],
        'currentCompany': 'Test Labs',
        'industryInvolvement': [1,2,3,4,5],
        'workCategories': [1,2,3],
        'linkedinUrl': 'https://linkedin.com/testuser',
        'bio': 'I am a test user.',
        'interestAreas': [1,2,3]
    }
    response = test_client.put('/signup', json=json)
    response_data = response.get_json()
    assert response_data == LoginResponse.missing_fields_builder(full_name=True)
    assert response.status_code == 400 # Bad request 

def test_signup_failure_missing_username(test_client):
    json = {
        'fullname': 'Test User1',
        'email': 'testuser1@gmail.com',
        'password': 'password',
        'techstack': [1,2,3,4,5],
        'currentCompany': 'Test Labs',
        'industryInvolvement': [1,2,3,4,5],
        'workCategories': [1,2,3],
        'linkedinUrl': 'https://linkedin.com/testuser',
        'bio': 'I am a test user.',
        'interestAreas': [1,2,3]
    }
    response = test_client.put('/signup', json=json)
    response_data = response.get_json()
    assert response_data == LoginResponse.missing_fields_builder(username=True)
    assert response.status_code == 400 # Bad request

def test_signup_failure_missing_password(test_client):
    json = {
        'fullname': 'Test User1',
        'username': 'testuser1',
        'email': 'testuser1@gmail.com',
        'techstack': [1,2,3,4,5],
        'currentCompany': 'Test Labs',
        'industryInvolvement': [1,2,3,4,5],
        'workCategories': [1,2,3],
        'linkedinUrl': 'https://linkedin.com/testuser',
        'bio': 'I am a test user.',
        'interestAreas': [1,2,3]
    }
    response = test_client.put('/signup', json=json)
    response_data = response.get_json()
    assert response_data == LoginResponse.missing_fields_builder(password=True)
    assert response.status_code == 400 # Bad request

def test_signup_failure_missing_current_company(test_client):
    with patch('rtt_data_app.utils.db_manager.DBManager.get_db_connection') as mock_get_db_connection:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn
        json = {
            'fullname': 'Test User1',
            'username': 'testuser1',
            'email': 'testuser1@gmail.com',
            'password': 'password',
            'techstack': [1,2,3,4,5],
            'industryInvolvement': [1,2,3,4,5],
            'workCategories': [1,2,3],
            'linkedinUrl': 'https://linkedin.com/testuser',
            'bio': 'I am a test user.',
            'interestAreas': [1,2,3]
        }
        response = test_client.put('/signup', json=json)
        response_data = response.get_json()
        assert response_data == LoginResponse.missing_fields_builder(current_company=True)
        assert response.status_code == 400 # Bad request

def test_login_with_username_success(test_client, generate_mock_token):
        login_json = {
            'username': 'elongates',
            'password': 'password'
        }
        login_response = test_client.post('/login', json=login_json)
        login_response_data = login_response.get_json()
        assert login_response.status_code == 200
        # Remove times for proper asserts
        login_response_data['userDetails'].pop('accountCreationTime', None)
        login_response_data['userDetails'].pop('accountUpdateTime', None)

        assert login_response_data == LoginResponse.ELON_LOGIN_RESPONSE

def test_login_with_username_fail_wrong_password(test_client):
    with patch('rtt_data_app.utils.db_manager.DBManager.get_db_connection') as mock_get_db_connection:
        login_json = {
            'username': 'elongates',
            'password': 'ihatetesla'
        }
        with patch('rtt_data_app.auth.token_auth.Authorizer.generate_token') as mock_token:
            mock_token.return_value = {'MockToken': 'MockToken'}
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
        'username': 'elongates@example.com',
        'password': 'password'
    }
    login_response = test_client.post('/login', json=login_json)
    assert login_response.status_code == 200
    login_response_data = login_response.get_json()
    # Remove times for proper asserts
    login_response_data['userDetails'].pop('accountCreationTime', None)
    login_response_data['userDetails'].pop('accountUpdateTime', None)

    assert login_response_data == LoginResponse.ELON_LOGIN_RESPONSE
        
def test_login_with_email_fail_wrong_password(test_client):
    login_json = {
        'username': 'elongates@example.com',
        'password': 'password1'
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