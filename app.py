from flask import Flask
from flask_cors import CORS
from routes.feed import feed_bp
from routes.comment import comment_bp
from routes.vendor import vendor_bp
from routes.user import user_bp, update_trie
from routes.post import post_bp
from config import ProductionConfig


def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_class)

    app.register_blueprint(feed_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(vendor_bp)
    app.register_blueprint(post_bp)
    return app

app = create_app(config_class=ProductionConfig)

if __name__ == '__main__':
    update_trie() # Initial Trie population
    app.run()
