import os

class Config(object):
    # Common Configurations like SECRET_KEY
    DEBUG = False
    TESTING = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    DEBUG = True
    LOG_PATH = 'logs/'
    SSL_CONFIG = {
        'ssl': {
        'ca': '/config/global-bundle.pem'  # Path to the downloaded AWS RDS certificate
        }
    }
    SQLALCHEMY_ENGINE_OPTIONS = {'connect_args':SSL_CONFIG}

class DevelopmentConfig(Config):
    DEBUG = True
    DB_HOST = 'localhost'
    DB_USER = 'dev_user'
    DB_PASSWORD = 'dev_password'
    DB_NAME = 'dev_db'

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:////Users/raghavmaini/Desktop/rttMVP/rttDataService/tests/sqlite/test_database.db'
    LOG_PATH = 'tests/logs'