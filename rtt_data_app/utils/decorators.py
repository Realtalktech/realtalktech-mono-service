from flask import request, jsonify
from functools import wraps
import jwt

def process_token(token):
    token = token.split(" ")[1]  # Remove "Bearer" prefix to get the actual token
    data = jwt.decode(token, 'mock_secret_key', algorithms=["HS256"])
    user_id = data['sub']
    return user_id

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({"error": "Token is missing or invalid!"}), 403
        try:
            user_id = process_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401
        
        return f(user_id, *args, **kwargs)
    return decorated_function
