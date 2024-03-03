import mock

class MockInputs:
    MOCK_HEADER = {'Authorization': 'Bearer Mock Token'}


class LoginResponse:
    SIGNUP_SUCCESS = {
        "message": "Signup successful",
        "token": {"MockToken": "MockToken"}
    }

    INCORRECT_PASSWORD_RESPONSE = {
        "error":"Unauthorized",
        "message":"401 Unauthorized: Incorrect Password"}

    INVALID_EMAIL_RESPONSE = {
        "error":"Unauthorized",
        "message":"401 Unauthorized: Invalid Email"
        }

    LOCALHOST_EMAIL_RESPONSE = {
        "error":"Bad request",
        "message":"400 Bad Request: The domain name localhost.com does not send email."
    }

    ONBOARDING_RESPONSE = {"industries": 
                           [
                               {"id": 1, "industry_name": "AdTech"}, 
                               {"id": 2, "industry_name": "Angel or VC Firm"}, 
                               {"id": 3, "industry_name": "AI"}, 
                               {"id": 4, "industry_name": "Automation"}
                            ], 
                            "interestAreas": 
                            [
                                {"id": 1, "interest_area_name": "Sales Tools"}, 
                                {"id": 2, "interest_area_name": "Marketing"}, 
                                {"id": 3, "interest_area_name": "Analytics Tools & Software"}
                            ], "subscriptionAreas": 
                            [
                                {"category_name": "AI", "id": 1}, 
                                {"category_name": "Engineering", "id": 2}, 
                                {"category_name": "Marketing", "id": 4}, 
                                {"category_name": "Operations", "id": 3}
                            ], 
                            "techstack": [
                                {"id": 1, "vendor_name": "Salesforce"}, 
                                {"id": 2, "vendor_name": "Snowflake"}, 
                                {"id": 3, "vendor_name": "Databricks"}, 
                                {"id": 4, "vendor_name": "Datadog"}
                            ]
                        }


    def get_unrecognized_user_profile_response(username):
        return {
            "error": "Bad request",
            "message": f"400 Bad Request: User with username {username} not found"
        }

    class ELON:
        def __init__(self):
            self.login_creds = {
                'username': 'elongates',
                'password': 'password'
            }
            self.login_response = {
                "message":"Login successful",
                "token":{"MockToken":"MockToken"},
                'userDetails': {
                    'bio': None,
                    'currentCompany': 'SuperchargedSoftware',
                    'email': 'elongates@example.com',
                    'fullname': 'Elon Gates',
                    'username': 'elongates',
                    'id': 1,
                    'industryInvolvement': [
                        {'id': 1, 'name': 'AdTech'}, 
                        {'id': 2, 'name': 'Angel or VC Firm'}, 
                        {'id': 3, 'name': 'AI'}, 
                        {'id': 4, 'name': 'Automation'}, 
                    ], 
                    'interestAreas': [
                        {'id': 1, 'name': 'Sales Tools'}, 
                        {'id': 2, 'name': 'Marketing'}, 
                        {'id': 3, 'name': 'Collaboration & Productivity'}, 
                        {'id': 4, 'name': 'Commerce'}, 
                    ], 
                    'linkedinUrl': None, 
                    'occupationalAreas': [
                        {'id': 1, 'name': 'AI'}, 
                        {'id': 2, 'name': 'Engineering'}, 
                        {'id': 3, 'name': 'Operations'}
                    ], 
                    'techstack': []
                    }
                }
            self.bio = None
            self.email = 'elongates@example.com'
            self.password = 'password'
            self.fullname = self.login_response['userDetails']['fullname']
            self.username = self.login_response['userDetails']['username']
            self.id = self.login_response['userDetails']['id']
            self.industry_involvement_ids = [
                id['id'] for id in self.login_response['userDetails']['industryInvolvement']
                ]
            self.industry_involvement_names = [
                name['name'] for name in self.login_response['userDetails']['industryInvolvement']
                ]
            self.interest_area_ids = [
                id['id'] for id in self.login_response['userDetails']['interestAreas']
                ]
            self.interest_area_names = [
                name['name'] for name in self.login_response['userDetails']['interestAreas']
                ]
            self.occupational_area_ids = [
                id['id'] for id in self.login_response['userDetails']['occupationalAreas']
                ]
            self.occupational_area_names = [
                name['name'] for name in self.login_response['userDetails']['occupationalAreas']
                ]


    class MockUser:
        def __init__(self):
            self.id = 1
        
        def get_signup_data(self, success = True):
            signup_data = {
                'fullname': f'Test User {self.id}',
                'username': f'testuser{self.id}',
                'email': f'testuser{self.id}@gmail.com',
                'password': 'password',
                'techstack': ["Salesforce", "Snowflake", "Databricks", "Datadog"],
                'currentCompany': 'Test Labs',
                'industryInvolvement': [1, 2, 3, 4, 5],
                'workCategories': [1, 2, 3],
                'linkedinUrl': f'https://linkedin.com/testuser{self.id}',
                'bio': 'I am a test user.',
                'interestAreas': [1, 2, 3]
            }
            if success:
                self.id += 1
            return signup_data
        
        def get_raw_insert_data(self):
            username =  f'mockuser{self.id}'
            fullname = f'Mock User {self.id}'
            email = f'mock{self.id}@example.com'
            current_company = 'Test Labs'
            password = 'test'
            id_stub = self.id
            self.id += 1
            return username, fullname, email, current_company, password, id_stub
        

    def missing_fields_builder( 
                               full_name=False,
                               username=False,
                               email=False,
                               password=False,
                               current_company=False
                               ):
        missing_fields = []
        if full_name:
            missing_fields.append('fullname')
        if username:
            missing_fields.append('username')
        if email:
            missing_fields.append('email')
        if password:
            missing_fields.append('password')
        if current_company:
            missing_fields.append('currentCompany')

        if len(missing_fields) > 0:
            missing_fields_str = missing_fields_str = ', '.join(missing_fields)  # Convert the list to a comma-separated string
            error_message = f"Missing required fields: {missing_fields_str}"
        
        return {
            "error": "Bad request",
            "message": "400 Bad Request: " + error_message
        }


class PostResponse:
    VOTE_POST_SUCCESS_RESPONSE = {
        "message": "Post vote toggled successfully"
    }

    VOTE_POST_FAIL_MISSING_ID = {
        "error": "Bad request",
        "message": "400 Bad Request: error: postId is required"
    }

    VOTE_POST_FAIL_MISSING_INTENTION = {
        "error": "Bad request",
        "message": "400 Bad Request: error: vote intention is required"
    }

    EDIT_UNOWNED_POST_RESPONSE = {
    "error": "Bad request",
    'message': '400 Bad Request: Post not found or you do not have permission to edit this post'
    }

    MISSING_POST_ID_RESPONSE = {
        "error": "Bad request",
        "message": "400 Bad Request: Post ID is required"
    }

    def __init__(self):
       self.EXPECTED_POST_ID = 6
        
    def create_post_response(self):
        response = {
            'message': 'Post created successfully',
            'post_id': self.EXPECTED_POST_ID
        }
        self.EXPECTED_POST_ID += 1
        return response

    def missing_fields_response_builder(self,
            title = False,
            body = False,
            is_anonymous = False
    ):
        missing_fields = []
        if title: missing_fields.append('title')
        if body: missing_fields.append('body')
        if is_anonymous: missing_fields.append('anonymity status')
        if len(missing_fields) > 0:
            missing_fields_str = missing_fields_str = ', '.join(missing_fields)  # Convert the list to a comma-separated string
            error_message = f"Missing required fields: {missing_fields_str}"
        return {
            "error": "Bad request",
            "message": "400 Bad Request: " + error_message
        }

    def edit_post_response(self):
        return {
            "message": "Post updated successfully"
        }


class VendorResponse:
    DISCOVER_GROUPS_RESPONSE = [
        {"icon": "", "id": 1, "name": "Sales Tools"}, 
        {"icon": "", "id": 2, "name": "Marketing"}, 
        {"icon": "", "id": 3, "name": "Collaboration & Productivity"}, 
        {"icon": "", "id": 4, "name": "Commerce"}]

    CATEGORY_ONE_RESPONSE = {
        "metadata": {"count": 10, "discoverCategoryId": 1, "page": 1, "totalItems": 4, "totalPages": 1}, 
        "vendors": [
            {"description": "Datadog", "id": 4, "vendorHomepageUrl": None, "vendorLogoUrl": None, "vendorName": "Datadog", "vendorType": "Datadog"}, 
            {"description": "Databricks", "id": 3, "vendorHomepageUrl": None, "vendorLogoUrl": None, "vendorName": "Databricks", "vendorType": "Databricks"}, 
            {"description": "Snowflake", "id": 2, "vendorHomepageUrl": None, "vendorLogoUrl": None, "vendorName": "Snowflake", "vendorType": "Snowflake"}, 
            {"description": "Salesforce", "id": 1, "vendorHomepageUrl": None, "vendorLogoUrl": None, "vendorName": "Salesforce", "vendorType": "Salesforce"}]}
    
    VENDOR_ONE_RESPONSE = {"description": "Salesforce", "homepageUrl": None, "hq": None, "id": 1, "logoUrl": None, "name": "Salesforce", "totalEmployees": None}


class CommentResponse:
    POST_ONE_COMMENTS_RESPONSE = {
        "comments": [
            {
                "commentText": "Maybe I should try it so I can sell more cars too", 
                "id": 2, 
                "taggedUsernames": [], 
                "totalDownvotes": 0, 
                "totalUpvotes": 0, 
                "userVote": False, 
                "username": "marybarra"
            }, 
            {
                "commentText": "Salesforce is a great tool!", 
                "id": 1, 
                "taggedUsernames": [], 
                "totalDownvotes": 0,
                "totalUpvotes": 1, 
                "userVote": False, 
                "username": "billmusk"
            }
        ], 
        "metadata": {
            "count": 10, 
            "page": 1, 
            "postId": 1, 
            "searcherUserId": 5
        }
    }