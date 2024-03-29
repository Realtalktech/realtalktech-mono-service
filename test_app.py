from flask import Flask
from routes.feed import feed_bp
from routes.comment import comment_bp
from routes.vendor import vendor_bp
from routes.user import user_bp
from routes.post import post_bp
from config import TestingConfig

def create_test_app(config_class=TestingConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    app.register_blueprint(feed_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(vendor_bp)
    app.register_blueprint(post_bp)
    return app

if __name__ == '__main__':
    app = create_test_app(config_class=TestingConfig)
