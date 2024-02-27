import os

class Config(object):
    # Common Configurations like SECRET_KEY
    DEBUG = False
    TESTING = False

class ProductionConfig(Config):
    DB_HOST = 'realtalktechrdsstack-realtalktechdbinstance-c7ciisdczocf.cnqm62ueodz0.us-east-1.rds.amazonaws.com'
    DB_USER = 'admin'
    DB_PASSWORD = 'ReallyRealAboutTech123!'
    DB_NAME = 'RealTalkTechDB'
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
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


