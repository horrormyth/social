from flask import render_template
from peewee import DoesNotExist

from views import app


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')


@app.errorhandler(DoesNotExist)
def not_found(error):
    return render_template('404.html')
