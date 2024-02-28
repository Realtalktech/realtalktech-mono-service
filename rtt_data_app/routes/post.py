from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
from rtt_data_app.utils import DBManager, token_required
from werkzeug.exceptions import BadRequest, Unauthorized, InternalServerError
from rtt_data_app.utils import Post

post_bp = Blueprint('post_bp', __name__)
db_manager = DBManager()


@post_bp.route('/makePost', methods=['POST'])
@token_required
def make_post(user_id):
    if not user_id:
        raise Unauthorized("error: User not authenticated")    
    data = request.json
    title = data.get('title')
    body = data.get('body')
    categories = data.get('categories', [])  # List of category ids
    is_anonymous = data.get('isAnonymous')
    vendors = data.get('vendors', []) # List of vendor ids

    if not (title and body) or (is_anonymous is None):
        missing_fields = []
        if not title: missing_fields.append('title')
        if not body: missing_fields.append('body')
        if is_anonymous is None: missing_fields.append('anonymity status')
        if len(missing_fields) > 0:
            missing_fields_str = missing_fields_str = ', '.join(missing_fields)  # Convert the list to a comma-separated string
            error_message = f"Missing required fields: {missing_fields_str}"
        raise BadRequest(error_message)

    post_id = Post().create_post_and_fetch_id(author_id=user_id, 
                                              title=title, 
                                              body=body, 
                                              category_ids=categories, 
                                              is_anonymous=is_anonymous, 
                                              tagged_vendor_ids=vendors)
    return jsonify({"message": "Post created successfully", "post_id": post_id}), 201

@post_bp.route('/editPost', methods=['PUT'])
@token_required
def edit_post(user_id):
    if not user_id:
        raise Unauthorized("error: User not authenticated")  # 401 Unauthorized
    
    data:dict = request.json
    post_id = data.get('postId')
    new_title = data.get('title')
    new_body = data.get('body')
    new_categories = set(data.get('categories', []))  # List of new category ids
    new_vendors = set(data.get('vendors', [])) # List of new vendor ids

    if not post_id:
        raise BadRequest("Post ID is required")
    
    post = Post()
    post.edit_post(
        user_id, post_id, new_title, new_body, new_categories, new_vendors
    )
    
    return jsonify({"message": "Post updated successfully"}), 200

@post_bp.route('/upvotePost', methods=['PUT'])
@token_required
def upvote_post(user_id):
    if not user_id:
        raise Unauthorized("error: User not authenticated")
    
    data:dict = request.json
    post_id = data.get('postId')
    is_downvote = data.get('isDownvote')

    if not post_id:
        raise BadRequest("error: postId is required")
    if is_downvote is None:
        raise BadRequest("error: vote intention is required")
    
    Post().toggle_post_vote(post_id, user_id, is_downvote)

    return jsonify({"message": "Post vote toggled successfully"}), 200