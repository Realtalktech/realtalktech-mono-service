class MockInputs:
    MOCK_HEADER = {'Authorization': 'Bearer Mock Token'}


class LoginResponse:
    SIGNUP_SUCCESS = {
        "message": "Signup successful",
        "token": {"MockToken": "MockToken"}
    }
    
    ELON_LOGIN_RESPONSE = {
                "message":"Login successful",
                "token":{"MockToken":"MockToken"},
                'userDetails': {
                    'bio': None,
                    'currentCompany': 'SuperchargedSoftware',
                    'email': 'elongates@example.com',
                    'fullName': 'Elon Gates',
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
                    'techstack': []
                    }
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
    