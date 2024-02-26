class Config(object):
    # Common Configurations like SECRET_KEY
    DEBUG = False
    TESTING = False

class ProductionConfig(Config):
    DB_HOST = 'realtalktechrdsstack-realtalktechdbinstance-c7ciisdczocf.cnqm62ueodz0.us-east-1.rds.amazonaws.com'
    DB_USER = 'admin'
    DB_PASSWORD = 'ReallyRealAboutTech123!'
    DB_NAME = 'RealTalkTechDB'
    LOG_PATH = '/var/log/flask_app'

class DevelopmentConfig(Config):
    DEBUG = True
    DB_HOST = 'localhost'
    DB_USER = 'dev_user'
    DB_PASSWORD = 'dev_password'
    DB_NAME = 'dev_db'

class TestingConfig(Config):
    DB_HOST = 'localhost'
    DB_USER = 'user'
    DB_PASSWORD = 'password'
    DB_NAME = 'test_db'
    LOG_PATH = 'tests/logs'

