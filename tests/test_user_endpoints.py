from functools import wraps
import json
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest
from unittest.mock import patch
from rtt_data_app.app import app, create_app, db
from rtt_data_app.models import User, PublicVendor, UserPublicVendor, UserPublicVendorEndorsement
from tests.databuilder import DataBuilder, DataInserter, UserFactory
from config import TestingConfig
import pytest
from unittest.mock import patch

from tests.commons import MockInputs, LoginResponse

mock_user = LoginResponse.MockUser()

@pytest.fixture(scope='session')
def test_client():
    """Fixture to set up Flask app for testing"""
    # Setup Flask app for testing
    app = create_app(config_class=TestingConfig)

    # Initialize testing DB
    with app.app_context():
        DataBuilder.init_test_database()
        DataInserter().init_test_database()
        # Create a test client for Flask application
        with app.test_client() as testing_client:
            yield testing_client

@pytest.fixture(scope='function', autouse=True)
def authorize_as_new_user(test_client):
    """Fixture to create a new user and make requests on their behalf."""
    user_generator = UserFactory.create_and_teardown_users(test_client, db)
    users_list = next(user_generator)
    user= users_list[0]
    token_return_value = user.id
    with patch('rtt_data_app.auth.decorators.process_token', return_value = token_return_value):
        yield user

def test_get_user_public_profile_success(test_client, authorize_as_new_user):
    # Setup mock data
    requesting_user:User = authorize_as_new_user
    requested_user_generator = UserFactory.create_and_teardown_users(test_client, db, 1)
    requested_user:User = next(requested_user_generator)[0]
    id_stub = UserFactory.get_id_stub(requested_user)

    # Assign tech_stack to mock user
    vendors = [PublicVendor(id=i) for i in range(1, 4)]
    user_vendor_associations = [UserPublicVendor(user_id=requested_user.id, vendor_id=vendor.id) for vendor in vendors]
    db.session.add_all(user_vendor_associations)
    db.session.commit()

    # requesting_user endorses requested_user in areas 1 and 2
    endorsement = UserPublicVendorEndorsement(endorser_user_id=requesting_user.id, endorsee_user_id=requested_user.id, vendor_id=1)
    db.session.add(endorsement)
    endorsement = UserPublicVendorEndorsement(endorser_user_id=requesting_user.id, endorsee_user_id=requested_user.id, vendor_id=2)
    db.session.add(endorsement)
    db.session.commit()

    # Perform the request
    response = test_client.get(f'/user/testuser{id_stub}', headers=MockInputs.MOCK_HEADER)
    data = response.get_json()

    print(json.dumps(data, indent=2))


    # Assertions
    assert response.status_code == 200
    assert data['userDetails']['username'] == f'testuser{id_stub}'
    assert data['userDetails']['bio'] == None
    assert data['userDetails']['currentCompany'] == 'Test Labs'
    assert data['userDetails']['linkedinUrl'] == None
    assert data['userDetails']['fullname'] == f'Test User {id_stub}'
    assert len(data['vendors']) == 3
    assert all(vendor['endorsedByRequester'] for vendor in data['vendors'] if vendor['id'] in {1, 2})
    assert all(not vendor['endorsedByRequester'] for vendor in data['vendors'] if vendor['id'] == 3)

def test_get_user_private_profile_success(test_client, authorize_as_new_user):
    # Setup mock data
    user:User = authorize_as_new_user
    id_stub = UserFactory.get_id_stub(user)
    vendors = [PublicVendor(id=i) for i in range(1, 4)]

    # Assign tech_stack to mock user
    user_vendor_associations = [UserPublicVendor(user_id=user.id, vendor_id=vendor.id) for vendor in vendors]
    db.session.add_all(user_vendor_associations)
    db.session.commit()

    # Create endorsing user
    endorser_user:User = next(UserFactory.create_and_teardown_users(test_client, db))[0]

    # Endorsing user endorses mock user in vendors 1 and 2
    endorsements = [
        UserPublicVendorEndorsement(endorser_user_id=endorser_user.id, endorsee_user_id=user.id, vendor_id=vendor.id)
        for vendor in vendors[:2]
    ]
    db.session.add_all(endorsements)
    db.session.commit()
    db.session.refresh(endorser_user)

    # Perform the request
    response = test_client.get(f'/user/{user.username}', headers=MockInputs.MOCK_HEADER)
    data = response.get_json()

    print(json.dumps(data, indent=2))


    # Assertions
    assert response.status_code == 200
    assert data['userDetails']['username'] == f'testuser{id_stub}'
    assert data['userDetails']['email'] == f'test{id_stub}@example.com'
    assert data['userDetails']['bio'] == None
    assert data['userDetails']['currentCompany'] == 'Test Labs'
    assert data['userDetails']['linkedinUrl'] == None
    assert data['userDetails']['fullname'] == f'Test User {id_stub}'
    assert len(data['vendors']) == 3
    assert all(vendor['totalEndorsements'] == 1 for vendor in data['vendors'] if vendor['id'] in {1, 2})
    assert all(vendor['userEndorsements'][0]['id'] == endorser_user.id for vendor in data['vendors'] if vendor['id'] in {1, 2})
    assert all(vendor['userEndorsements'][0]['username'] == endorser_user.username for vendor in data['vendors'] if vendor['id'] in {1, 2})
    assert all(vendor['totalEndorsements'] == 0 for vendor in data['vendors'] if vendor['id'] in {3})
    assert all(len(vendor['userEndorsements']) == 0 for vendor in data['vendors'] if vendor['id'] in {3})

def test_get_user_profile_fail_nonexistent_user(test_client):
    # Perform the request
    response = test_client.get(f'/user/nonexistentUser', headers=MockInputs.MOCK_HEADER)
    data = response.get_json()

    print(json.dumps(data, indent=2))

    # Assertions
    assert response.status_code == 400
    assert data == LoginResponse.get_unrecognized_user_profile_response("nonexistentUser")

def test_edit_profile_net_new_vendors_success(test_client, authorize_as_new_user):
    # Create a new mock user
    user:User = authorize_as_new_user
    # Create new vendors for the mock user
    new_vendors = [UserPublicVendor(vendor_id=i) for i in range(1,3)]

    # Associate vendors with the mock user
    user.user_vendor_associations.extend(new_vendors)
    db.session.commit()

    # Create mock endorsing user
    endorsing_user:User = next(UserFactory.create_and_teardown_users(test_client, db))[0]

    # Endorse the mock user for the first two tech stack vendors by user with id=1
    endorsements = [
        UserPublicVendorEndorsement(endorser_user_id=endorsing_user.id, endorsee_user_id=user.id, vendor_id=vendor)
        for vendor in range(1,3)
    ]
    db.session.add_all(endorsements)
    db.session.commit()

    # Prepare new data for profile update
    new_profile_data = {
        "fullname": "Updated Name",
        "email": "updated@example.com",
        "bio": "Updated bio here",
        "linkedin": "https://linkedin.com/updated",
        "techstack": ["Tech0", "Tech2"],  # Net new, these should be added to PublicVendor
        "currentCompany": "Updated Company"
    }

    # Call the editProfile endpoint
    response = test_client.put('/editProfile', json=new_profile_data, headers=MockInputs.MOCK_HEADER)
    assert response.status_code == 200

    # Fetch the updated user and verify changes
    updated_user:User = User.query.filter_by(id=user.id).one()
    assert updated_user.full_name == "Updated Name"
    assert updated_user.email == "updated@example.com"
    assert updated_user.bio == "Updated bio here"
    assert updated_user.linkedin_url == "https://linkedin.com/updated"
    assert updated_user.current_company == "Updated Company"
    assert {vendor.vendor_id for vendor in updated_user.user_vendor_associations} == {5,6}
    new_tech_stack_names = []
    for vendor in updated_user.user_vendor_associations:
        new_tech_stack_names.append(PublicVendor.query.filter_by(id=vendor.vendor_id).first().vendor_name)
    assert {name for name in new_tech_stack_names} == {"Tech0", "Tech2"}

    # Verify removal of tech stacks and associated endorsements (endorsements will now stay)
    removed_vendor = PublicVendor.query.filter_by(vendor_name="Salesforce").first()
    assert removed_vendor not in updated_user.user_vendor_associations
    removed_endorsements = UserPublicVendorEndorsement.query.filter_by(endorsee_user_id=user.id, vendor_id=removed_vendor.id).all()
    assert len(removed_endorsements) == 1  # Confirm endorsements for removed tech still exist

def test_edit_password_success(test_client, authorize_as_new_user):
    response = test_client.put(
        '/editPassword',
        json = {
            'oldPassword': 'password',
            'newPassword': 'newpassword'
        },
        headers=MockInputs.MOCK_HEADER
    )
    data = response.get_json()
    assert response.status_code == 200
    assert data == {
        "message": "Password updated successfully"
    }
    updated_user = User.query.filter_by(id=authorize_as_new_user.id).one()
    assert check_password_hash(updated_user.password, 'newpassword')

def test_edit_password_fail_missing_old_password(test_client, authorize_as_new_user):
    response = test_client.put(
        '/editPassword',
        json = {
            'newPassword': 'newpassword'
        },
        headers=MockInputs.MOCK_HEADER
    )
    data = response.get_json()
    assert response.status_code == BadRequest.code
    assert data == {
        "error": "Bad request",
        "message": "400 Bad Request: error: Missing old password"
    }

def test_edit_password_fail_missing_new_password(test_client, authorize_as_new_user):
    response = test_client.put(
        '/editPassword',
        json = {
            'oldPassword': 'password'
        },
        headers=MockInputs.MOCK_HEADER
    )
    data = response.get_json()
    assert response.status_code == BadRequest.code
    assert data == {
        "error": "Bad request",
        "message": "400 Bad Request: error: Missing new password"
    }

def test_edit_password_fail_incorrect_old_password(test_client, authorize_as_new_user):
    response = test_client.put(
        '/editPassword',
        json = {
            'oldPassword': 'newPassword',
            'newPassword': 'password'
        },
        headers=MockInputs.MOCK_HEADER
    )
    data = response.get_json()
    assert response.status_code == BadRequest.code
    assert data == {
        "error": "Bad request",
        "message": "400 Bad Request: error: Old Password is Incorrect"
    } 

def insert_new_user_with_tech_stack(test_client):
    """Insert a new user with an endorsable tech stack"""
    # Using test_client to stay within context
    user = User(username='testendorsee', 
                email='testendorsee@example.com', 
                full_name='Test Endorsee',
                current_company='Test Labs',
                password=generate_password_hash('password'))
    db.session.add(user)
    db.session.commit()
    # Add vendors 1-3 to user profile
    techstack = [UserPublicVendor(vendor_id=i) for i in range(1,3)]
    user.user_vendor_associations.extend(techstack)
    db.session.commit()
    db.session.refresh(user)
    return user

def test_endorse_user_success(test_client, authorize_as_new_user):
    endorser_user = authorize_as_new_user
    endorsee_user = insert_new_user_with_tech_stack(test_client)
    # Endorsee 'endorsee_user' in vendor 1
    request = {
        'endorseeUserId': endorsee_user.id,
        'vendorId': 1
    }
    response = test_client.put(
        '/endorse',
        json=request,
        headers=MockInputs.MOCK_HEADER
    )
    data = response.get_json()
    
    assert data == {
        "message": "Profile endorsed successfully"
    }

    # Confirm endorsement propagated through DBs
    endorsement_obj = UserPublicVendorEndorsement.query.filter_by(endorser_user_id=endorser_user.id, endorsee_user_id=endorsee_user.id, vendor_id=1).first()
    assert endorsement_obj.vendor_id == 1
    assert type(endorsement_obj.endorser) == User
    assert type(endorsement_obj.endorsee) == User
    assert endorser_user.given_endorsements[0].endorsee_user_id == endorsee_user.id
    assert endorsee_user.received_endorsements[0].endorser_user_id == endorser_user.id
    assert response.status_code == 200
    registered_public_vendors = UserPublicVendor.query.filter_by(user_id=endorsee_user.id).all()
    db.session.delete(endorsement_obj)
    for obj in registered_public_vendors:
        db.session.delete(obj)
    db.session.commit()
    db.session.delete(endorsee_user)
    db.session.commit()

def test_endorse_user_fail_missing_endorsee_id(test_client, authorize_as_new_user):
    request = {
        'vendorId': 1
    }
    response = test_client.put(
        '/endorse',
        json=request,
        headers=MockInputs.MOCK_HEADER
    )
    data = response.get_json()
    print(json.dumps(data, indent=2))
    
    assert data == {
        "error": "Bad request",
        "message": "400 Bad Request: Endorsee User Id is required"
    }
    assert response.status_code == BadRequest.code

def test_endorse_user_fail_missing_vendor_id(test_client, authorize_as_new_user):
    request = {
        'endorseeUserId': 1
    }
    response = test_client.put(
        '/endorse',
        json=request,
        headers=MockInputs.MOCK_HEADER
    )
    data = response.get_json()
    print(json.dumps(data, indent=2))
    
    assert data == {
        "error": "Bad request",
        "message": "400 Bad Request: Vendor Id is required"
    }
    assert response.status_code == BadRequest.code

def test_endorse_user_fail_nonexistent_endorseee(test_client, authorize_as_new_user):
    request = {
        'endorseeUserId': 9000,
        'vendorId': 1
    }
    response = test_client.put(
        '/endorse',
        json=request,
        headers=MockInputs.MOCK_HEADER
    )
    data = response.get_json()
    print(json.dumps(data, indent=2))
    
    assert data == {
        "error": "Bad request",
        "message": "400 Bad Request: Endorsee does not exist!"
    }
    assert response.status_code == BadRequest.code

def test_endorse_user_fail_unregistered_vendor(test_client, authorize_as_new_user):
    endorser_user = authorize_as_new_user
    endorsee_user = insert_new_user_with_tech_stack(test_client)
    # Endorsee 'endorsee_user' in vendor 4 (they only have vendors 1 - 3)
    request = {
        'endorseeUserId': endorsee_user.id,
        'vendorId': 4
    }
    response = test_client.put(
        '/endorse',
        json=request,
        headers=MockInputs.MOCK_HEADER
    )
    data = response.get_json()
    print(json.dumps(data, indent=2))
    
    assert data == {
        "error": "Bad request",
        "message": "400 Bad Request: User does not have vendor in their techstack"
    }
    assert response.status_code == BadRequest.code

    # Cleanup
    registered_public_vendors = UserPublicVendor.query.filter_by(user_id=endorsee_user.id).all()
    for obj in registered_public_vendors:
        db.session.delete(obj)
    db.session.commit()
    db.session.delete(endorsee_user)
    db.session.commit()