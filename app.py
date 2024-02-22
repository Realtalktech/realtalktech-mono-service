from flask import Flask
from flask_cors import CORS
from routes.feed import feed_bp
from routes.comment import comment_bp
from routes.vendor import vendor_bp
from routes.login import login_bp
from routes.user import user_bp
from routes.post import post_bp
from config import ProductionConfig

import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    handler = RotatingFileHandler('flask_app.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logging.getLogger('werkzeug').addHandler(handler)  # For werkzeug server logging
    app.logger.addHandler(handler)

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_class)

    app.register_blueprint(feed_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(vendor_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(login_bp)
    return app

app = create_app(config_class=ProductionConfig)

if __name__ == '__main__':
    # update_trie() # Initial Trie population
    setup_logging()  # Call this before your routes are initialized
    app.run()
