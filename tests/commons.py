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

    ONBOARDING_RESPONSE = {
        "industries": [{"id": 1,"industry_name": "AdTech"},
            {"id": 2,"industry_name": "Angel or VC Firm"},
            {"id": 3,"industry_name": "AI"},
            {"id": 4,"industry_name": "Automation"},
            {"id": 5,"industry_name": "Big Data"},
            {"id": 6,"industry_name": "Biotech"},
            {"id": 7,"industry_name": "Blockchain"},
            {"id": 8,"industry_name": "Business Intelligence"},
            {"id": 9,"industry_name": "Cannabis"},
            {"id": 10,"industry_name": "Cloud"},
            {"id": 11,"industry_name": "Consulting"},
            {"id": 12,"industry_name": "Web/Internet"},
            {"id": 13,"industry_name": "Crypto"},
            {"id": 14,"industry_name": "Cybersecurity"},
            {"id": 15,"industry_name": "Data Privacy"},
            {"id": 16,"industry_name": "Database"},
            {"id": 17,"industry_name": "eCommerce"},
            {"id": 18,"industry_name": "Edtech"},
            {"id": 19,"industry_name": "FinTech"},
            {"id": 20,"industry_name": "Gaming"},
            {"id": 21,"industry_name": "Healthtech"},
            {"id": 22,"industry_name": "HR Tech"},
            {"id": 23,"industry_name": "IaaS"},
            {"id": 24,"industry_name": "Insurance"},
            {"id": 25,"industry_name": "IoT"},
            {"id": 26,"industry_name": "Legal Tech"},
            {"id": 27,"industry_name": "Logistics"},
            {"id": 28,"industry_name": "Machine Learning"},
            {"id": 29,"industry_name": "Manufacturing"},
            {"id": 30,"industry_name": "MarTech"},
            {"id": 31,"industry_name": "Metaverse"},
            {"id": 32,"industry_name": "Mobile"},
            {"id": 33,"industry_name": "Music"},
            {"id": 34,"industry_name": "Natural Language Processing"},
            {"id": 35,"industry_name": "NFT"},
            {"id": 36,"industry_name": "Payments"},
            {"id": 37,"industry_name": "Pharmaceutical"},
            {"id": 38,"industry_name": "Procurement"},
            {"id": 39,"industry_name": "Professional Services"},
            {"id": 40,"industry_name": "Real Estate"},
            {"id": 41,"industry_name": "Sales"},
            {"id": 42,"industry_name": "Software"},
            {"id": 43,"industry_name": "Sports"},
            {"id": 44,"industry_name": "Travel"},
            {"id": 45,"industry_name": "Web3"},
            {"id": 46,"industry_name": "Other"}
        ],
        "interestAreas": [{"id": 1,"interest_area_name": "Sales Tools"},
            {"id": 2,"interest_area_name": "Marketing"},
            {"id": 3,"interest_area_name": "Analytics Tools & Software"},
            {"id": 4,"interest_area_name": "CAD & PLM"},
            {"id": 5,"interest_area_name": "Collaboration & Productivity"},
            {"id": 6,"interest_area_name": "Commerce"},
            {"id": 7,"interest_area_name": "Customer Service"},
            {"id": 8,"interest_area_name": "Data Privacy"},
            {"id": 9,"interest_area_name": "Design"},
            {"id": 10,"interest_area_name": "Development"},
            {"id": 11,"interest_area_name": "Digital Advertising"},
            {"id": 12,"interest_area_name": "ERP"},
            {"id": 13,"interest_area_name": "Governance, Risk & Compliance"},
            {"id": 14,"interest_area_name": "Hosting"},
            {"id": 15,"interest_area_name": "HR"},
            {"id": 16,"interest_area_name": "IT Infrastructure"},
            {"id": 17,"interest_area_name": "IT Management"},
            {"id": 18,"interest_area_name": "Office"},
            {"id": 19,"interest_area_name": "Security"},
            {"id": 20,"interest_area_name": "Supply Chain & Logistics"},
            {"id": 21,"interest_area_name": "Vertical Industry"},
            {"id": 22,"interest_area_name": "Collaboration"},
            {"id": 23,"interest_area_name": "Customer Management"},
            {"id": 24,"interest_area_name": "Revenue Operations"},
            {"id": 25,"interest_area_name": "Payments"},
            {"id": 26,"interest_area_name": "Accounting"},
            {"id": 27,"interest_area_name": "Learning Management System"},
            {"id": 28,"interest_area_name": "Robotic Process Automation"},
            {"id": 29,"interest_area_name": "Artificial Intelligence"}
        ],
        "subscriptionAreas": [{"category_name": "AI","id": 1},
            {"category_name": "Community","id": 13},
            {"category_name": "Customer Success","id": 6},
            {"category_name": "Data","id": 7},
            {"category_name": "Engineering","id": 2},
            {"category_name": "Finance","id": 10},
            {"category_name": "Founder","id": 12},
            {"category_name": "HR & Talent","id": 9},
            {"category_name": "Leadership/Exec","id": 11},
            {"category_name": "Marketing","id": 4},
            {"category_name": "Operations","id": 3},
            {"category_name": "Product","id": 8},
            {"category_name": "Sales","id": 5}
        ],
        "techstack": [{"id": 1,"vendor_name": "Salesforce"},
            {"id": 2,"vendor_name": "Snowflake"},
            {"id": 3,"vendor_name": "Databricks"},
            {"id": 4,"vendor_name": "Datadog"},
            {"id": 5,"vendor_name": "Roblox"},
            {"id": 6,"vendor_name": "Apple"},
            {"id": 7,"vendor_name": "AWS"},
            {"id": 8,"vendor_name": "GCP"},
            {"id": 9,"vendor_name": "Azure"},
            {"id": 10,"vendor_name": "HTC"}
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
    DISCOVER_GROUPS_RESPONSE = [{"icon": "", "id": 1, "name": "Sales Tools"}, 
    {"icon": "", "id": 2, "name": "Marketing"}, 
    {"icon": "", "id": 3, "name": "Analytics Tools & Software"}, 
    {"icon": "", "id": 4, "name": "CAD & PLM"}, 
    {"icon": "", "id": 5, "name": "Collaboration & Productivity"}, 
    {"icon": "", "id": 6, "name": "Commerce"}, 
    {"icon": "", "id": 7, "name": "Content Management"}, 
    {"icon": "", "id": 8, "name": "Customer Service"}, 
    {"icon": "", "id": 9, "name": "Data Privacy"}, 
    {"icon": "", "id": 10, "name": "Design"}, 
    {"icon": "", "id": 11, "name": "Development"}, 
    {"icon": "", "id": 12, "name": "Digital Advertising Tech"}, 
    {"icon": "", "id": 13, "name": "ERP"}, 
    {"icon": "", "id": 14, "name": "Governance, Risk & Compliance"}, 
    {"icon": "", "id": 15, "name": "Hosting"}, 
    {"icon": "", "id": 16, "name": "HR"}, 
    {"icon": "", "id": 17, "name": "IT Infrastructure"}, 
    {"icon": "", "id": 18, "name": "IT Management"}, 
    {"icon": "", "id": 19, "name": "Security"}, 
    {"icon": "", "id": 20, "name": "Supply Chains & Logistics"}, 
    {"icon": "", "id": 21, "name": "Vertical Industry"}]

    CATEGORY_ONE_RESPONSE = {
        "metadata": {"count": 10, "discoverCategoryId": 1, "page": 1, "totalItems": 10, "totalPages": 1}, 
        "vendors": [
            {"description": "HTC", 
             "id": 10, 
             "vendorHomepageUrl": None, 
             "vendorLogoUrl": None, 
             "vendorName": "HTC", 
             "vendorType": "HTC"
            }, 
            {"description": "Azure", 
             "id": 9, 
             "vendorHomepageUrl": None, 
             "vendorLogoUrl": None, 
             "vendorName": "Azure", 
             "vendorType": "Azure"
            }, 
            {"description": "GCP", 
             "id": 8, 
             "vendorHomepageUrl": None, 
             "vendorLogoUrl": None, 
             "vendorName": "GCP", 
             "vendorType": "GCP"
            }, 
            {"description": "AWS", 
             "id": 7, 
             "vendorHomepageUrl": None, 
             "vendorLogoUrl": None, 
             "vendorName": "AWS", 
             "vendorType": "AWS"
            }, 
            {"description": "Apple", 
             "id": 6, 
             "vendorHomepageUrl": None, 
             "vendorLogoUrl": None, 
             "vendorName": "Apple", 
             "vendorType": "Apple"
            }, 
            {"description": "Roblox", 
             "id": 5, 
             "vendorHomepageUrl": None, 
             "vendorLogoUrl": None, 
             "vendorName": "Roblox", 
             "vendorType": "Roblox"
            }, 
            {"description": "Datadog", 
             "id": 4, 
             "vendorHomepageUrl": None, 
             "vendorLogoUrl": None, 
             "vendorName": "Datadog", 
             "vendorType": "Datadog"
            }, 
            {"description": "Databricks", 
             "id": 3, 
             "vendorHomepageUrl": None, 
             "vendorLogoUrl": None, 
             "vendorName": "Databricks", 
             "vendorType": "Databricks"}, 
            {"description": "Snowflake", 
             "id": 2, 
             "vendorHomepageUrl": None, 
             "vendorLogoUrl": None, 
             "vendorName": "Snowflake", 
             "vendorType": "Snowflake"}, 
            {"description": "Salesforce", 
             "id": 1, 
             "vendorHomepageUrl": None, 
             "vendorLogoUrl": None, 
             "vendorName": "Salesforce", 
             "vendorType": "Salesforce"
             }
            ]
        }
    
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