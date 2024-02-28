from functools import wraps
import json
from unittest.mock import patch
from rtt_data_app.app import app, create_app, db
from rtt_data_app.models import User, PublicVendor, UserPublicVendor, UserPublicVendorEndorsement
from tests.databuilder import Databuilder, DataInserter
from config import TestingConfig
from functools import wraps
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
        Databuilder.init_test_database()
        inserter = DataInserter()
        # Create a test client for Flask application
        with app.test_client() as testing_client:
            yield testing_client

# Automatically bypasses token check, authorizing inputted user_id
@pytest.fixture(autouse=True)
def bypass_token_required(request):
    """Fixture to bypass the token_required decorator."""
    token_return_value = getattr(request, 'param', 1)
    with patch('rtt_data_app.auth.decorators.process_token', return_value = token_return_value):
        yield

@pytest.mark.parametrize('bypass_token_required', [1], indirect=True) # Make request from user_id = 1
def test_get_user_public_profile_success(test_client):
    # Setup mock data
    username,full_name,email,current_company, password, id_stub = mock_user.get_raw_insert_data()
    user = User(username = username, 
                full_name = full_name,
                email = email,
                current_company = current_company,
                password = password)
    vendors = [PublicVendor(id=i) for i in range(1, 4)]
    db.session.add(user)
    db.session.commit()

    # Assign tech_stack to mock user
    user_vendor_associations = [UserPublicVendor(user_id=user.id, vendor_id=vendor.id) for vendor in vendors]
    db.session.add_all(user_vendor_associations)
    db.session.commit()

    # User_id 1 (elongates) endorses 'mockuser' in areas 1 and 2
    endorsements = [
        UserPublicVendorEndorsement(endorser_user_id=1, endorsee_user_id=user.id, vendor_id=vendor.id)
        for vendor in vendors[:2]
    ]
    db.session.add_all(endorsements)
    db.session.commit()

    # Perform the request
    response = test_client.get(f'/user/mockuser{id_stub}', headers=MockInputs.MOCK_HEADER)
    data = response.get_json()


    # Assertions
    assert response.status_code == 200
    assert data['userDetails']['username'] == f'mockuser{id_stub}'
    assert data['userDetails']['bio'] == None
    assert data['userDetails']['currentCompany'] == 'Test Labs'
    assert data['userDetails']['linkedinUrl'] == None
    assert data['userDetails']['fullname'] == f'Mock User {id_stub}'
    assert len(data['vendors']) == 3
    assert all(vendor['endorsedByRequester'] for vendor in data['vendors'] if vendor['id'] in {1, 2})
    assert all(not vendor['endorsedByRequester'] for vendor in data['vendors'] if vendor['id'] == 3)

# Make request from user_id = 6 (expected from mock user creation albeit hacky)
@pytest.mark.parametrize('bypass_token_required', [6], indirect=True) 
def test_get_user_private_profile_success(test_client):
    # Setup mock data
    username,full_name,email,current_company, password, id_stub = mock_user.get_raw_insert_data()

    user = User(username = username, 
                full_name = full_name,
                email = email,
                current_company = current_company,
                password = password)
    vendors = [PublicVendor(id=i) for i in range(1, 4)]
    db.session.add(user)
    db.session.commit()

    # Assign tech_stack to mock user
    user_vendor_associations = [UserPublicVendor(user_id=user.id, vendor_id=vendor.id) for vendor in vendors]
    db.session.add_all(user_vendor_associations)
    db.session.commit()

    # User_id 1 (elongates) endorses 'mockuser' in areas 1 and 2
    endorsements = [
        UserPublicVendorEndorsement(endorser_user_id=1, endorsee_user_id=user.id, vendor_id=vendor.id)
        for vendor in vendors[:2]
    ]
    db.session.add_all(endorsements)
    db.session.commit()

    # Perform the request
    response = test_client.get(f'/user/{user.username}', headers=MockInputs.MOCK_HEADER)
    data = response.get_json()

    # Assertions
    assert response.status_code == 200
    assert data['userDetails']['username'] == f'mockuser{id_stub}'
    assert data['userDetails']['email'] == f'mock{id_stub}@example.com'
    assert data['userDetails']['bio'] == None
    assert data['userDetails']['currentCompany'] == 'Test Labs'
    assert data['userDetails']['linkedinUrl'] == None
    assert data['userDetails']['fullname'] == f'Mock User {id_stub}'
    assert len(data['vendors']) == 3
    assert all(vendor['totalEndorsements'] == 1 for vendor in data['vendors'] if vendor['id'] in {1, 2})
    assert all(vendor['userEndorsements'][0]['id'] == LoginResponse.ELON().id for vendor in data['vendors'] if vendor['id'] in {1, 2})
    assert all(vendor['userEndorsements'][0]['username'] == LoginResponse.ELON().username for vendor in data['vendors'] if vendor['id'] in {1, 2})
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

# Make request from user_id = 7 (expected from mock user creation albeit hacky)
@pytest.mark.parametrize('bypass_token_required', [7], indirect=True) 
def test_edit_profile_net_new_vendors_success(test_client):
    # Create a new mock user
    username, fullname, email, current_company, password, id_stub = mock_user.get_raw_insert_data()
    new_user = User(username=f"mockuser{id_stub}", full_name=fullname, email=email, current_company=current_company, password=password)
    db.session.add(new_user)
    db.session.commit()

    # Create new vendors for the mock user
    new_vendors = [UserPublicVendor(vendor_id=i) for i in range(1,3)]

    # Associate vendors with the mock user
    new_user.user_vendor_associations.extend(new_vendors)
    db.session.commit()

    # Endorse the mock user for the first two tech stack vendors by user with id=1
    endorsements = [
        UserPublicVendorEndorsement(endorser_user_id=1, endorsee_user_id=new_user.id, vendor_id=vendor)
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
    response = test_client.put('/editProfile', json=new_profile_data, headers={"Authorization": "Bearer valid-token"})

    assert response.status_code == 200

    # Fetch the updated user and verify changes
    updated_user = User.query.filter_by(id=new_user.id).one()
    assert updated_user.full_name == "Updated Name"
    assert updated_user.email == "updated@example.com"
    assert updated_user.bio == "Updated bio here"
    assert updated_user.linkedin_url == "https://linkedin.com/updated"
    assert updated_user.current_company == "Updated Company"
    assert {vendor.vendor_id for vendor in updated_user.user_vendor_associations} == {11,12}
    new_tech_stack_names = []
    for vendor in updated_user.user_vendor_associations:
        new_tech_stack_names.append(PublicVendor.query.filter_by(id=vendor.vendor_id).first().vendor_name)
    assert {name for name in new_tech_stack_names} == {"Tech0", "Tech2"}

    # Verify removal of tech stacks and associated endorsements (endorsements will now stay)
    removed_vendor = PublicVendor.query.filter_by(vendor_name="Salesforce").first()
    assert removed_vendor not in updated_user.user_vendor_associations
    removed_endorsements = UserPublicVendorEndorsement.query.filter_by(endorsee_user_id=new_user.id, vendor_id=removed_vendor.id).all()
    assert len(removed_endorsements) == 1  # Confirm endorsements for removed tech still exist


