from flask import Flask, jsonify, request
import pymysql
from get_routes import get_bp
from post_put_routes import post_put_bp
import pymysql.cursors
from config import DevelopmentConfig, ProductionConfig, TestingConfig

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.register_blueprint(get_bp)
    app.register_blueprint(post_put_bp)
    return app
    

if __name__ == '__main__':
    app = create_app(config_class=ProductionConfig)
