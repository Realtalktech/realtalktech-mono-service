import os

class Config(object):
    # Common Configurations like SECRET_KEY
    DEBUG = False
    TESTING = False
    
print("COOL2")

class ProductionConfig(Config):
    DB_HOST = os.environ.get('DB_HOST')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_NAME')
    SSL_CA = 'config/amazon-rds-ca-cert.pem'

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
