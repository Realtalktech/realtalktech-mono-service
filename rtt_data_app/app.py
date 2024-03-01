from flask import Flask, jsonify
from werkzeug.exceptions import BadRequest, Unauthorized, InternalServerError, NotFound
from flask_cors import CORS
from rtt_data_app.models import db
from config import ProductionConfig, TestingConfig

from rtt_data_app.utils.log_config import setup_global_logging
setup_global_logging(TestingConfig.LOG_PATH) 

from rtt_data_app.routes import feed_bp, comment_bp, vendor_bp, login_bp, user_bp, post_bp

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

    db.init_app(app)

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
    def handle_internal_server_error(e):
        response = e.get_response()
        response.data = jsonify({"error": "Internal Server Error", "message": str(e)}).data
        response.content_type = "application/json"
        return response
    
    @app.errorhandler(NotFound)
    def handle_not_found_error(e):
        response = e.get_response()
        response.data = jsonify({"error": "Not Found Error", "message": str(e)}).data
        response.content_type = "application/json"
        return response

    return app

app = create_app(config_class=TestingConfig)

if __name__ == '__main__':
    # update_trie() # Initial Trie population
    app.run()
