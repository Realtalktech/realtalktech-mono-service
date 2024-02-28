from flask import request, jsonify
from functools import wraps
import jwt

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("Token required called")
        token = request.headers.get('Authorization')
        print(f"Received token: {token}")
        if not token or not token.startswith('Bearer '):
            return jsonify({"error": "Token is missing or invalid!"}), 403
        try:
            token = token.split(" ")[1]  # Remove "Bearer" prefix to get the actual token
            data = jwt.decode(token, 'mock_secret_key', algorithms=["HS256"])
            user_id = data['sub']
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401
        
        return f(user_id, *args, **kwargs)
    return decorated_function
