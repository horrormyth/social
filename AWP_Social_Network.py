from flask import Flask,g
from flask.ext.login import LoginManager
import models

DEBUG =True
PORT =8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'j\x0c\xbf[\x91\xdd\xf2$\xe3`y\xfb\xc0\x8b\xa8\xbb>*f\x1a\\\xe8E\xacF\x8a\xeeD~\tP\xae'
login_manager = LoginManager()
login_manager.init_app(app) # passing whole app into the loginmanager instance
login_manager.login_view ='login'  #if not logged in redirect it to the login view

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist: #from peweee (DoesNot Exist)
        return None

#Defining global database connection in before and After Request
@app.before_request
def before_request():
    # Database Connection before every reqeust
    g.db = models.DATABASE
    g.db.connect()

@app.after_request
def after_request(response):
    #Close the database Connection
    g.db.close()
    return response

if __name__ == '__main__':  #Run the App
    models.initialize() # initiallize the initialize method which will create the tables from models.py
    #create users
    models.User.create_users(
        name = 'myth',
        email= 'horrormyth@gmail.com',
        password = 'password',
        admin = True
    )
    app.run(debug=DEBUG,host=HOST,port=PORT)