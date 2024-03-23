import os

class Config(object):
    # Common Configurations like SECRET_KEY
    DEBUG = False
    TESTING = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    DEBUG = True
    LOG_PATH = '/var/log/flask_app'

class DevelopmentConfig(Config):
    DEBUG = True
    DB_HOST = 'localhost'
    DB_USER = 'dev_user'
    DB_PASSWORD = 'dev_password'
    DB_NAME = 'dev_db'

class TestingConfig(Config):
    # file_path = os.path.abspath()
    SQLALCHEMY_DATABASE_URI = 'sqlite:////Users/raghavmaini/Desktop/rttMVP/rttDataService/tests/sqlite/test_database.db'
    LOG_PATH = 'tests/logs'


