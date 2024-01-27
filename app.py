from flask import Flask, jsonify, request
import pymysql
from get_routes import get_bp
from post_put_routes import post_put_bp
import pymysql.cursors
from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

app.register_blueprint(get_bp)
app.register_blueprint(get_bp)


def create_app():
    return app

if __name__ == '__main__':
    app.run(debug=True)
