class Config(object):
    DEBUG = False
    TESTING = False
    # Common Configurations like DATABASE_URI

class ProductionConfig(Config):
    DATABASE_URI = 'mysql+pymysql://user:pwd@production_host/db_name'

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URI = 'mysql+pymysql://user:pwd@localhost/db_name'

class TestingConfig(Config):
    TESTING = True
    DATABASE_URI = 'mysql+pymysql://user:pwd@localhost/test_db_name'
