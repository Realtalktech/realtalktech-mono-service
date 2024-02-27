import os
import sys
topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)
from app import app, create_app, db
from tests.databuilder import Databuilder, DataInserter
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
        inserter = DataInserter()
    
    # Create a test client for Flask application
    with app.test_client() as testing_client:
        yield testing_client

# @patch('app.auth.token_required', return_value=lambda x:x)
def test_signup_success(test_client):
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
    with patch('auth.token_auth.Authorizer.generate_token', return_value={'MockToken': 'MockToken'}):
        response = test_client.put('/signup', json=signup_data)
        response_data = response.get_json()
        assert response_data == {"message": "Signup successful", "token": {"MockToken": "MockToken"}}
        assert response.status_code == 201

def test_signup_failure_email_no_stub(test_client):
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
        login_json = {
            'username': 'elongates',
            'password': 'password'
        }
        with patch('auth.token_auth.Authorizer.generate_token') as mock_token:
            mock_token.return_value = {'MockToken': 'MockToken'}
            login_response = test_client.post('/login', json=login_json)
            login_response_data = login_response.get_json()
            assert login_response.status_code == 200
            # Remove times for proper asserts
            login_response_data['userDetails'].pop('accountCreationTime', None)
            login_response_data['userDetails'].pop('accountUpdateTime', None)

            assert login_response_data == {
                "message":"Login successful",
                "token":{"MockToken":"MockToken"},
                'userDetails': {
                    'bio': None,
                    'currentCompany': 'SuperchargedSoftware',
                    'email': 'elongates@example.com',
                    'fullName': 'Elon Gates',
                    'id': 1,
                    'industryInvolvement': [
                        {'id': 1, 'name': 'AdTech'}, 
                        {'id': 2, 'name': 'Angel or VC Firm'}, 
                        {'id': 3, 'name': 'AI'}, 
                        {'id': 4, 'name': 'Automation'}, 
                        {'id': 5, 'name': 'Big Data'}, 
                        {'id': 6, 'name': 'Biotech'}, 
                        {'id': 7, 'name': 'Blockchain'}, 
                        {'id': 8, 'name': 'Business Intelligence'}, 
                        {'id': 9, 'name': 'Cannabis'}, 
                        {'id': 10, 'name': 'Cloud'}, 
                        {'id': 11, 'name': 'Consulting'}
                    ], 
                    'interest_areas': [
                        {'id': 1, 'name': 'Sales Tools'}, 
                        {'id': 2, 'name': 'Marketing'}, 
                        {'id': 3, 'name': 'Analytics Tools & Software'}, 
                        {'id': 4, 'name': 'CAD & PLM'}, 
                        {'id': 5, 'name': 'Collaboration & Productivity'}, 
                        {'id': 6, 'name': 'Commerce'}, 
                        {'id': 7, 'name': 'Customer Service'}
                    ], 
                    'linkedinUrl': None, 
                    'occupationalAreas': [
                        {'id': 1, 'name': 'AI'}, 
                        {'id': 2, 'name': 'Engineering'}, 
                        {'id': 3, 'name': 'Operations'}
                    ], 
                    'techstack': [], 
                    'username': 'elongates'
                    }
                }

def test_login_with_username_fail_wrong_password(test_client):
    with patch('utils.db_manager.DBManager.get_db_connection') as mock_get_db_connection:
        login_json = {
            'username': 'elongates',
            'password': 'ihatetesla'
        }
        with patch('auth.token_auth.Authorizer.generate_token') as mock_token:
            mock_token.return_value = {'MockToken': 'MockToken'}
            login_response = test_client.post('/login', json=login_json)
            assert login_response.status_code == 401
            assert login_response.data == b'{"error":"Unauthorized","message":"401 Unauthorized: Incorrect Password"}\n'

def test_login_with_username_fail_nonexistent_user(test_client):
    login_json = {
        'username': 'joebiden',
        'password': 'sleepy'
    }
    login_response = test_client.post('/login', json=login_json)
    assert login_response.status_code == 401
    assert login_response.data == b'{"error":"Unauthorized","message":"401 Unauthorized: Invalid Username"}\n'

def test_login_with_email_success(test_client):
    login_json = {
        'username': 'elongates@example.com',
        'password': 'password'
    }
    with patch('auth.token_auth.Authorizer.generate_token') as mock_token:
        mock_token.return_value = {'MockToken': 'MockToken'}
        login_response = test_client.post('/login', json=login_json)
        print(login_response.data)
        assert login_response.status_code == 200
        login_response_data = login_response.get_json()
        # Remove times for proper asserts
        login_response_data['userDetails'].pop('accountCreationTime', None)
        login_response_data['userDetails'].pop('accountUpdateTime', None)

        assert login_response_data == {
            "message":"Login successful",
            "token":{"MockToken":"MockToken"},
            'userDetails': {
                'bio': None,
                'currentCompany': 'SuperchargedSoftware',
                'email': 'elongates@example.com',
                'fullName': 'Elon Gates',
                'id': 1,
                'industryInvolvement': [
                    {'id': 1, 'name': 'AdTech'}, 
                    {'id': 2, 'name': 'Angel or VC Firm'}, 
                    {'id': 3, 'name': 'AI'}, 
                    {'id': 4, 'name': 'Automation'}, 
                    {'id': 5, 'name': 'Big Data'}, 
                    {'id': 6, 'name': 'Biotech'}, 
                    {'id': 7, 'name': 'Blockchain'}, 
                    {'id': 8, 'name': 'Business Intelligence'}, 
                    {'id': 9, 'name': 'Cannabis'}, 
                    {'id': 10, 'name': 'Cloud'}, 
                    {'id': 11, 'name': 'Consulting'}
                ], 
                'interest_areas': [
                    {'id': 1, 'name': 'Sales Tools'}, 
                    {'id': 2, 'name': 'Marketing'}, 
                    {'id': 3, 'name': 'Analytics Tools & Software'}, 
                    {'id': 4, 'name': 'CAD & PLM'}, 
                    {'id': 5, 'name': 'Collaboration & Productivity'}, 
                    {'id': 6, 'name': 'Commerce'}, 
                    {'id': 7, 'name': 'Customer Service'}
                ], 
                'linkedinUrl': None, 
                'occupationalAreas': [
                    {'id': 1, 'name': 'AI'}, 
                    {'id': 2, 'name': 'Engineering'}, 
                    {'id': 3, 'name': 'Operations'}
                ], 
                'techstack': [], 
                'username': 'elongates'
                }
            }
        
def test_login_with_email_fail_wrong_password(test_client):
    login_json = {
        'username': 'elongates@example.com',
        'password': 'password1'
    }
    with patch('auth.token_auth.Authorizer.generate_token') as mock_token:
        mock_token.return_value = {'MockToken': 'MockToken'}
        login_response = test_client.post('/login', json=login_json)
        assert login_response.status_code == 401
        assert login_response.data == b'{"error":"Unauthorized","message":"401 Unauthorized: Incorrect Password"}\n'

def test_login_with_email_fail_nonexistent_user(test_client):
    login_json = {
        'username': 'joe@biden.com',
        'password': 'sleepysleepy'
    }
    
    with patch('auth.token_auth.Authorizer.generate_token') as mock_token:
        mock_token.return_value = {'MockToken': 'MockToken'}
        login_response = test_client.post('/login', json=login_json)
        assert login_response.status_code == 401
        assert login_response.data == b'{"error":"Unauthorized","message":"401 Unauthorized: Invalid Email"}\n'