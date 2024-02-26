import os
import sys
topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)
from app import app, create_app
from tests import Databuilder
from config import TestingConfig
# from utils import db_manager, DBManager
import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from werkzeug.security import generate_password_hash
import datetime

@pytest.fixture(scope='module')
def test_client():
    # Setup Flask app for testing
    app = create_app(config_class=TestingConfig)

    # Initialize testing DB
    with app.app_context():
        Databuilder.init_test_database()
    
    # Create a test client for Flask application
    with app.test_client() as testing_client:
        yield testing_client

# @patch('app.auth.token_required', return_value=lambda x:x)
def test_signup_success(test_client):
    with patch('utils.db_manager.DBManager.get_db_connection') as mock_get_db_connection:
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
            'currentCompany': 'Test Labs',
            'industryInvolvement': [1,2,3,4,5],
            'workCategories': [1,2,3],
            'linkedinUrl': 'https://linkedin.com/testuser',
            'bio': 'I am a test user.',
            'interestAreas': [1,2,3]
        }
        with patch('auth.token_auth.Authorizer.generate_token') as mock_token:
            mock_token.return_value = {'MockToken': 'MockToken'}
            response = test_client.put('/signup', json=json)
            print(response.data)
            assert response.data == b'{"message":"Signup successful","token":{"MockToken":"MockToken"}}\n'
            assert response.status_code == 201

def test_signup_failure_email_no_stub(test_client):
    with patch('utils.db_manager.DBManager.get_db_connection') as mock_get_db_connection:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn
        json = {
            'fullname': 'Test User1',
            'username': 'testuser1',
            'email': 'testuser1',
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
        assert response.data == b'{"error":"Bad request","message":"400 Bad Request: The email address is not valid. It must have exactly one @-sign."}\n'
        assert response.status_code == 400 # Bad request 

def test_signup_failure_missing_fullname(test_client):
    with patch('utils.db_manager.DBManager.get_db_connection') as mock_get_db_connection:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn
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
        assert response.data == b'{"error":"Bad request","message":"400 Bad Request: Missing required fields: fullname"}\n'
        assert response.status_code == 400 # Bad request 

def test_signup_failure_missing_username(test_client):
    with patch('utils.db_manager.DBManager.get_db_connection') as mock_get_db_connection:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn
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
        assert response.data == b'{"error":"Bad request","message":"400 Bad Request: Missing required fields: username"}\n'
        assert response.status_code == 400 # Bad request

def test_signup_failure_missing_password(test_client):
    with patch('utils.db_manager.DBManager.get_db_connection') as mock_get_db_connection:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn
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
        assert response.data == b'{"error":"Bad request","message":"400 Bad Request: Missing required fields: password"}\n'
        assert response.status_code == 400 # Bad request

def test_signup_failure_missing_current_company(test_client):
    with patch('utils.db_manager.DBManager.get_db_connection') as mock_get_db_connection:
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
        assert response.data == b'{"error":"Bad request","message":"400 Bad Request: Missing required fields: currentCompany"}\n'
        assert response.status_code == 400 # Bad request

def test_login_with_username_success(test_client):
    with patch('utils.db_manager.DBManager.get_db_connection') as mock_get_db_connection:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn
        login_json = {
            'username': 'testuser1',
            'password': 'password'
        }
        mock_cursor.fetchone.side_effect = [
            # Response to __fetch_login_credentials_by_username
            {'id': 1, 'password': generate_password_hash('password')},
            # Response to __get_user_details
            {'id': 1, 
             'full_name': 'Test User', 
             'username': 'testuser', 
             'current_company': 'Test Labs',
             'email': 'test@test.com',
             'linkedin_url': 'https://linkedin.com/testuser',
             'bio': 'I am a test user.',
            },
            # Response to __get_user_details/__fetch_account_creation_time
            {'creation_time': '2021-12-25 01:59:11.137'},
            # Response to__get_user_details/__fetch_account_update_time
            {'update_time': '2021-12-25 01:59:11.137'},
            # Response to __get_user_tech_stack/processing
            {'vendor_name': 'Salesforce'},
            # Response to __get_user_industry_involvement/processing
            {'industry_name': 'Sales'},
            # Response to __get_user_subscribed_discuss_categories/processing
            {'category_name': 'Engineering'},
            # Response to __get_user_interest_area/processing
            {'interest_area_name': 'AI'}
        ]
        mock_cursor.fetchall.side_effect = [
            # Response to __get_user_tech_stack
            [{'vendor_id': 1}],
            # Response to __get_user_industry_involvement
            [{'industry_id': 1}],
            # Response to __get_user_subscribed_discuss_categories
            [{'category_id': 2}],
            # Response to __get_user_interest_area
            [{'interest_area_id': 1}],
        ]
        with patch('auth.token_auth.Authorizer.generate_token') as mock_token:
            mock_token.return_value = {'MockToken': 'MockToken'}
            login_response = test_client.post('/login', json=login_json)
            connection = sqlite3.connect('tests/sqlite/test_database.db')
            cursor = connection.cursor()
            cursor.execute("""SELECT * FROM User WHERE username = 'testuser1'""")
            assert login_response.status_code == 200
            assert login_response.data == b'{"message":"Login successful","token":{"MockToken":"MockToken"},"userDetails":{"accountCreationTime":"2021-12-25 01:59:11.137","accountUpdateTime":"2021-12-25 01:59:11.137","bio":"I am a test user.","currentCompany":"Test Labs","email":"test@test.com","fullName":"Test User","id":1,"industryInvolvement":[{"id":1,"name":"Sales"}],"interest_areas":[{"id":1,"name":"AI"}],"linkedinUrl":"https://linkedin.com/testuser","occupationalAreas":[{"id":2,"name":"Engineering"}],"techstack":[{"id":1,"name":"Salesforce"}],"username":"testuser"}}\n'

def test_login_with_username_fail_wrong_password(test_client):
    with patch('utils.db_manager.DBManager.get_db_connection') as mock_get_db_connection:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn
        login_json = {
            'username': 'testuser1',
            'password': 'password'
        }
        mock_cursor.fetchone.side_effect = [
            # Response to __fetch_login_credentials_by_username
            {'id': 1, 'password': generate_password_hash('password1')},
            # Response to __get_user_details
            {'id': 1, 
             'full_name': 'Test User', 
             'username': 'testuser', 
             'current_company': 'Test Labs',
             'email': 'test@test.com',
             'linkedin_url': 'https://linkedin.com/testuser',
             'bio': 'I am a test user.',
            },
            # Response to __get_user_details/__fetch_account_creation_time
            {'creation_time': '2021-12-25 01:59:11.137'},
            # Response to__get_user_details/__fetch_account_update_time
            {'update_time': '2021-12-25 01:59:11.137'},
            # Response to __get_user_tech_stack/processing
            {'vendor_name': 'Salesforce'},
            # Response to __get_user_industry_involvement/processing
            {'industry_name': 'Sales'},
            # Response to __get_user_subscribed_discuss_categories/processing
            {'category_name': 'Engineering'},
            # Response to __get_user_interest_area/processing
            {'interest_area_name': 'AI'}
        ]
        mock_cursor.fetchall.side_effect = [
            # Response to __get_user_tech_stack
            [{'vendor_id': 1}],
            # Response to __get_user_industry_involvement
            [{'industry_id': 1}],
            # Response to __get_user_subscribed_discuss_categories
            [{'category_id': 2}],
            # Response to __get_user_interest_area
            [{'interest_area_id': 1}],
        ]
        with patch('auth.token_auth.Authorizer.generate_token') as mock_token:
            mock_token.return_value = {'MockToken': 'MockToken'}
            login_response = test_client.post('/login', json=login_json)
            assert login_response.status_code == 401
            assert login_response.data == b'{"error":"Unauthorized","message":"401 Unauthorized: Incorrect Password"}\n'

def test_login_with_username_fail_nonexistent_user(test_client):
    with patch('utils.db_manager.DBManager.get_db_connection') as mock_get_db_connection:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn
        login_json = {
            'username': 'testuser1',
            'password': 'password'
        }
        mock_cursor.fetchone.side_effect = [
            # Response to __fetch_login_credentials_by_username
            None
        ]
        with patch('auth.token_auth.Authorizer.generate_token') as mock_token:
            mock_token.return_value = {'MockToken': 'MockToken'}
            login_response = test_client.post('/login', json=login_json)
            assert login_response.status_code == 401
            assert login_response.data == b'{"error":"Unauthorized","message":"401 Unauthorized: Invalid Username"}\n'

def test_login_with_email_success(test_client):
    with patch('utils.db_manager.DBManager.get_db_connection') as mock_get_db_connection:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn
        login_json = {
            'username': 'testuser@test.com',
            'password': 'password'
        }
        mock_cursor.fetchone.side_effect = [
            # Response to __fetch_username_from_email
            {'username': 'testuser'},
            # Response to __fetch_login_credentials_by_username
            {'id': 1, 'password': generate_password_hash('password')},
            # Response to __get_user_details
            {'id': 1, 
             'full_name': 'Test User', 
             'username': 'testuser', 
             'current_company': 'Test Labs',
             'email': 'test@test.com',
             'linkedin_url': 'https://linkedin.com/testuser',
             'bio': 'I am a test user.',
            },
            # Response to __get_user_details/__fetch_account_creation_time
            {'creation_time': '2021-12-25 01:59:11.137'},
            # Response to__get_user_details/__fetch_account_update_time
            {'update_time': '2021-12-25 01:59:11.137'},
            # Response to __get_user_tech_stack/processing
            {'vendor_name': 'Salesforce'},
            # Response to __get_user_industry_involvement/processing
            {'industry_name': 'Sales'},
            # Response to __get_user_subscribed_discuss_categories/processing
            {'category_name': 'Engineering'},
            # Response to __get_user_interest_area/processing
            {'interest_area_name': 'AI'}
        ]
        mock_cursor.fetchall.side_effect = [
            # Response to __get_user_tech_stack
            [{'vendor_id': 1}],
            # Response to __get_user_industry_involvement
            [{'industry_id': 1}],
            # Response to __get_user_subscribed_discuss_categories
            [{'category_id': 2}],
            # Response to __get_user_interest_area
            [{'interest_area_id': 1}],
        ]
        with patch('auth.token_auth.Authorizer.generate_token') as mock_token:
            mock_token.return_value = {'MockToken': 'MockToken'}
            login_response = test_client.post('/login', json=login_json)
            connection = sqlite3.connect('tests/sqlite/test_database.db')
            cursor = connection.cursor()
            cursor.execute("""SELECT * FROM User WHERE username = 'testuser1'""")
            assert login_response.status_code == 200
            assert login_response.data == b'{"message":"Login successful","token":{"MockToken":"MockToken"},"userDetails":{"accountCreationTime":"2021-12-25 01:59:11.137","accountUpdateTime":"2021-12-25 01:59:11.137","bio":"I am a test user.","currentCompany":"Test Labs","email":"test@test.com","fullName":"Test User","id":1,"industryInvolvement":[{"id":1,"name":"Sales"}],"interest_areas":[{"id":1,"name":"AI"}],"linkedinUrl":"https://linkedin.com/testuser","occupationalAreas":[{"id":2,"name":"Engineering"}],"techstack":[{"id":1,"name":"Salesforce"}],"username":"testuser"}}\n'

def test_login_with_email_fail_wrong_password(test_client):
    with patch('utils.db_manager.DBManager.get_db_connection') as mock_get_db_connection:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn
        login_json = {
            'username': 'testuser1@gmail.com',
            'password': 'password'
        }
        mock_cursor.fetchone.side_effect = [
            # Response to __fetch_username_from_email
            {'username': 'testuser'},
            # Response to __fetch_login_credentials_by_username
            {'id': 1, 'password': generate_password_hash('password1')},
            # Response to __get_user_details
            {'id': 1, 
             'full_name': 'Test User', 
             'username': 'testuser', 
             'current_company': 'Test Labs',
             'email': 'test@test.com',
             'linkedin_url': 'https://linkedin.com/testuser',
             'bio': 'I am a test user.',
            },
            # Response to __get_user_details/__fetch_account_creation_time
            {'creation_time': '2021-12-25 01:59:11.137'},
            # Response to__get_user_details/__fetch_account_update_time
            {'update_time': '2021-12-25 01:59:11.137'},
            # Response to __get_user_tech_stack/processing
            {'vendor_name': 'Salesforce'},
            # Response to __get_user_industry_involvement/processing
            {'industry_name': 'Sales'},
            # Response to __get_user_subscribed_discuss_categories/processing
            {'category_name': 'Engineering'},
            # Response to __get_user_interest_area/processing
            {'interest_area_name': 'AI'}
        ]
        mock_cursor.fetchall.side_effect = [
            # Response to __get_user_tech_stack
            [{'vendor_id': 1}],
            # Response to __get_user_industry_involvement
            [{'industry_id': 1}],
            # Response to __get_user_subscribed_discuss_categories
            [{'category_id': 2}],
            # Response to __get_user_interest_area
            [{'interest_area_id': 1}],
        ]
        with patch('auth.token_auth.Authorizer.generate_token') as mock_token:
            mock_token.return_value = {'MockToken': 'MockToken'}
            login_response = test_client.post('/login', json=login_json)
            assert login_response.status_code == 401
            assert login_response.data == b'{"error":"Unauthorized","message":"401 Unauthorized: Incorrect Password"}\n'

def test_login_with_email_fail_nonexistent_user(test_client):
    with patch('utils.db_manager.DBManager.get_db_connection') as mock_get_db_connection:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn
        login_json = {
            'username': 'testuser1@gmail.com',
            'password': 'password'
        }
        mock_cursor.fetchone.side_effect = [
            # Response to __fetch_username_from_email
            None
        ]
        mock_cursor.fetchall.side_effect = [
            # Response to __get_user_tech_stack
            [{'vendor_id': 1}],
            # Response to __get_user_industry_involvement
            [{'industry_id': 1}],
            # Response to __get_user_subscribed_discuss_categories
            [{'category_id': 2}],
            # Response to __get_user_interest_area
            [{'interest_area_id': 1}],
        ]
        with patch('auth.token_auth.Authorizer.generate_token') as mock_token:
            mock_token.return_value = {'MockToken': 'MockToken'}
            login_response = test_client.post('/login', json=login_json)
            assert login_response.status_code == 401
            assert login_response.data == b'{"error":"Unauthorized","message":"401 Unauthorized: Invalid Email"}\n'