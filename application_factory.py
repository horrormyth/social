import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, request, abort
from flask_login import LoginManager
from peewee import SqliteDatabase, DoesNotExist

import models


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    _load_config(app, config_name)
    _setup_logging(app)
    # _init_db(app)
    login_manager = LoginManager()
    login_manager.login_view = 'social.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(userid):
        try:
            return models.User.get(models.User.id == userid)
        except DoesNotExist:
            return abort(403)

    _register_blue_print(app)
    return app


def _register_blue_print(app):
    from views import social as social_blueprint

    app.register_blueprint(social_blueprint)


def _load_config(app, config_name):
    app.config.from_object(config_name)


def _init_db(app):
    db_name = app.config['DB_NAME']
    sql_db = SqliteDatabase(db_name)
    with sql_db.database:
        sql_db.database.create_tables([models.User, models.Post, models.Relationship], safe=True)
    return sql_db


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.url = request.url
        record.remote_addr = request.remote_addr
        return super(RequestFormatter, self).format(record)


def _setup_logging(app):
    log_line = '[%(asctime)s]-%(remote_addr)s requested %(url)s %(levelname)s ' \
               'in %(module)s: at line %(lineno)d - %(message)s'
    formatter = RequestFormatter(log_line)
    handler = RotatingFileHandler('social_logs.log', maxBytes=10000, backupCount=1)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
