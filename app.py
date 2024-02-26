from flask import Flask, jsonify
from werkzeug.exceptions import BadRequest, Unauthorized, InternalServerError
from flask_cors import CORS
from config import ProductionConfig, TestingConfig
import os

from utils.log_config import setup_global_logging
setup_global_logging(TestingConfig.LOG_PATH) 

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

    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        response = e.get_response()
        response.data = jsonify({"error": "Bad request", "message": str(e)}).data
        response.content_type = "application/json"
        return response

    @app.errorhandler(Unauthorized)
    def handle_unauthorized(e):
        response = e.get_response()
        response.data = jsonify({"error": "Unauthorized", "message": str(e)}).data
        response.content_type = "application/json"
        return response

    @app.errorhandler(InternalServerError)
    def handle_unauthorized(e):
        response = e.get_response()
        response.data = jsonify({"error": "Unauthorized", "message": str(e)}).data
        response.content_type = "application/json"
        return response

    return app

app = create_app(config_class=ProductionConfig)





if __name__ == '__main__':
    # update_trie() # Initial Trie population
    app.run()
