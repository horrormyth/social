from flask import (Flask,g,render_template,flash,redirect,url_for)
from flask.ext.login import LoginManager

import models
import forms

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

@app.route('/register',methods=('GET','POST'))
def register():
    form = forms.RegistrationForm() #instance of registrationForm class
    if form.validate_on_submit(): #if validated and sumbitted
        flash('Registration Succesful','success') #second part is the message category (Creating)
        models.User.create_users(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html',form=form)

@app.route('/')
def index():
    return 'Hello Social'

if __name__ == '__main__':  #Run the App
    models.initialize() # initiallize the initialize method which will create the tables from models.py
    #create users
    try:
        models.User.create_users(
            username= 'myth',
            email= 'horrormyth@gmail.com',
            password = 'password',
            admin = True
        )
    except ValueError:
        pass
    app.run(debug=DEBUG,host=HOST,port=PORT)