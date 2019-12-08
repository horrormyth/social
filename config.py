import os


class Config:
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY',
                           "j\x0c\xbf[\x91\xdd\xf2$\xe3`y\xfb\xc0\x8b\xa8\xbb>*f\x1a\\\xe8E\xacF\x8a\xeeD~\tP\xae")
    DB_NAME = os.getenv('DB_NAME', 'awp_social.db')


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'


class TestingConfig(Config):
    DB_NAME = os.getenv('DB_NAME', 'awp_social.db')
    TESTING = True
    DEBUG = True
    ENV = 'testing'


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    ENV = 'production'
