from flask import Blueprint, jsonify, request
import pymysql
import pymysql.cursors
from utils import DBManager, token_required
from werkzeug.exceptions import BadRequest, Unauthorized, InternalServerError
from models import Post

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
        missing_fields = ''
        if not title: missing_fields += 'title '
        if not body: missing_fields += 'body '
        if is_anonymous is None: missing_fields += 'anonymity status '
        raise BadRequest(f"Missing required post information: {missing_fields}")

    post_id = Post().create_post_and_fetch_id(user_id, title, body, categories, is_anonymous, vendors)
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
    new_categories = set(data.get('categories', []))  # List of new category names
    new_vendors = set(data.get('vendors', [])) # List of new vendor names

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
    is_downvote = data.get('isDownvote', False) # False for upvote

    if not post_id:
        raise BadRequest("error: postId is required")
    if not is_downvote:
        raise BadRequest("error: vote intention is required")
    
    Post().toggle_post_vote(post_id, user_id, is_downvote)

    return jsonify({"message": "Post upvoted successfully"}), 200