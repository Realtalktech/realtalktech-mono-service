from flask import Blueprint, jsonify, request
from rtt_data_app.app import db
from rtt_data_app.models import Post, DiscussCategory, DiscoverVendor, PostDiscussCategory, PostDiscoverVendor, UserDiscussCategory, User, PostUpvote
from rtt_data_app.auth import token_required
from sqlalchemy.orm import aliased
from pprint import pprint

feed_bp = Blueprint('feed_bp', __name__)

@feed_bp.route('/feed', methods=['GET'])
@token_required
def get_feed(user_id):
    category_id = request.args.get('categoryId', type=int)  # None if "All" screen
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 10, type=int)

    # Aliases for clarity in joins
    PostCat = aliased(PostDiscussCategory)
    UserCat = aliased(UserDiscussCategory)

    query = db.session.query(
        Post.id, 
        Post.title, 
        Post.body, 
        Post.creation_time, 
        Post.update_time, 
        Post.user_id, 
        Post.is_anonymous,
        db.func.group_concat(DiscussCategory.category_name.distinct()).label('categories'),
        db.func.group_concat(DiscoverVendor.vendor_name.distinct()).label('vendors')
    ).select_from(Post).outerjoin(
        PostCat, Post.id == PostCat.post_id
    ).outerjoin(
        DiscussCategory, PostCat.category_id == DiscussCategory.id
    ).outerjoin(
        PostDiscoverVendor, Post.id == PostDiscoverVendor.post_id
    ).outerjoin(
        DiscoverVendor, PostDiscoverVendor.vendor_id == DiscoverVendor.id
    )

    # Filter based on category if provided, or user's subscribed categories otherwise
    if category_id:
        query = query.filter(DiscussCategory.id == category_id)
    else:
        query = query.filter(
            Post.id.in_(
                db.session.query(PostCat.post_id)
                .join(UserCat, UserCat.category_id == PostCat.category_id)
                .filter(UserCat.user_id == user_id)
            )
        )

    # Pagination and execution
    posts = query.group_by(Post.id).order_by(Post.creation_time.desc()).offset((page - 1) * count).limit(count).all()

    # Formatting results #numComments commentIds
    posts_data = []
    for post in posts:
        user = User.query.get(post.user_id) if not post.is_anonymous else None

        # Get comments
        post_obj = db.session.query(Post).get(post.id)
        num_comments = len(post_obj.comments)  # Now this should work correctly
        comment_ids = [comment.id for comment in post_obj.comments]

        # Get num_upvotes, num_downvotes, and user_vote
        num_upvotes = PostUpvote.query.filter_by(post_id=post.id, is_downvote=False).count()
        num_downvotes = PostUpvote.query.filter_by(post_id=post.id, is_downvote=True).count()
        user_vote:PostUpvote = PostUpvote.query.filter_by(post_id=post.id, user_id=user_id).first()
        user_vote_status = None
        if user_vote:
            user_vote_status = not user_vote.is_downvote


        posts_data.append({
            'id': post.id,
            'title': post.title,
            'body': post.body,
            'creationTime': post.creation_time.isoformat(),
            'updateTime': post.update_time.isoformat(),
            'user': {'id': user.id, 'username': user.username} if user else {'id': -1, 'username': 'anonymous'},
            'categories': post.categories.split(',') if post.categories else [],
            'vendors': post.vendors.split(',') if post.vendors else [],
            'numComments': num_comments,
            'commentIds': comment_ids,
            'numUpvotes': num_upvotes,
            'numDownvotes': num_downvotes,
            'userVote': user_vote_status
        })

    metadata = {
        'categoryId': category_id,
        'searcherUserId': user_id,
        'page': page,
        'count': count
    }

    return jsonify({"metadata": metadata, "posts": posts_data})
