from flask import render_template

from views import app


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')
