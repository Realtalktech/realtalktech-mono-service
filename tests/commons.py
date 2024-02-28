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
                        {'id': 5, 'name': 'Big Data'}, 
                        {'id': 6, 'name': 'Biotech'}, 
                        {'id': 7, 'name': 'Blockchain'}, 
                        {'id': 8, 'name': 'Business Intelligence'}, 
                        {'id': 9, 'name': 'Cannabis'}, 
                        {'id': 10, 'name': 'Cloud'}, 
                        {'id': 11, 'name': 'Consulting'}
                    ], 
                    'interestAreas': [
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
                'techstack': [1, 2, 3, 4, 5],
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
    