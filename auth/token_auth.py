import jwt
import datetime

class Authorizer():
    @classmethod
    def generate_token(cls,user_id):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=3), # expiration time
                'iat': datetime.datetime.utcnow(), #issue time
                'sub': user_id # Subject (user_id)
            }
            return jwt.encode(payload, 'mock_secret_key', algorithm='HS256') # MUST be changed for production
        except Exception as e:
            return str(e)