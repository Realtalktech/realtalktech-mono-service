from flask import Flask
from flask_cors import CORS
from config import ProductionConfig
import os

import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_directory = '/var/log/flask_app'  # Choose directory for logs
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    log_file = os.path.join(log_directory, 'flask_app.log')
    handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=3)
    formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    # Add handler to flask app logger and werkzeug
    logging.getLogger('werkzeug').addHandler(handler)  # For werkzeug server logging
    app.logger.addHandler(handler)

    # Set log level for both
    app.logger.setLevel(logging.INFO)
    logging.getLogger('werkzeug').setLevel(logging.INFO)

setup_logging()

from routes.feed import feed_bp
from routes.comment import comment_bp
from routes.vendor import vendor_bp
from routes.login import login_bp
from routes.user import user_bp
from routes.post import post_bp

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
    setup_logging()  # Call this before routes are initialized
    app.run()
