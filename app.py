import os

from flask import g
from flask_login import current_user

from application_factory import create_app
from base_model import sql_db


CONFIG_NAME = os.getenv('APP_SETTINGS', 'config.DevelopmentConfig')
app = create_app(CONFIG_NAME)


@app.before_request
def before_request():
    g.db = sql_db
    g.db.connect()
    g.user = current_user


@app.teardown_request
def teardown_request(response):
    g.db.close()
    return response


if __name__ == '__main__':
    app.run(use_reloader=True)
