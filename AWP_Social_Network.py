from flask import (Flask,g,render_template,flash,redirect,url_for,abort)
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import LoginManager,login_user,logout_user,login_required,current_user

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
    g.user = current_user

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

@app.route('/login',methods=('GET','POST')) #login view
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash('Your email or Password doesnt match','error')
        else:
            if check_password_hash(user.password,form.password.data):
                login_user(user) #creating sessions on users browser and giving the cookie
                flash('You are logged in','success')
                return redirect(url_for('index'))
            else:
                flash('Your email or Password doesnt match','error')
    return render_template('login.html',form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user() #delets the cookie (user cookie)
    flash('You are Logged Out','success')
    return redirect(url_for('index'))

@app.route('/new_post',methods=('GET','POST'))
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user._get_current_object(),
                           content = form.content.data.strip())
        flash('Message Posted','success')
        return redirect(url_for('index'))
    return render_template('post.html',form=form)


@app.route('/')
def index():
    stream = models.Post.select().limit(100)
    return render_template('stream.html', stream = stream)

@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None):
    template = 'stream.html'
    if username and username != current_user.username:
        try:
            user = models.User.select().where(models.User.username**username).get()
        except models.DoesNotExist:
            abort(404)  #404 IF NOT EXIST THROW 404 ERROR
        else:
            stream = user.posts.limit(100)
    else:
        stream = current_user.get_stream().limit(100)
        user = current_user
    if username:
        template ='user_stream.html'

    return render_template(template,stream=stream,user=user)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    posts = models.Post.select().where(models.Post.id == post_id) #select all the post from that user i follow
    if posts.count() == 0:
        abort(404) #if post is not in range throw 404
    return render_template('stream.html',stream=posts)

@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
        to_user = models.User.get(models.User.username ** username)
    except models.DoesNotExist:
        abort(404)  #if user doesnt exists throw 404 error
    else:
        try:models.Relationship.create(
            from_user =g.user._get_current_object(),
            to_user = to_user
        )
        except models.IntegrityError:
            pass
        else:
            flash('You are now following {}!'.format(to_user.username),'success')
    return redirect(url_for('stream', username=to_user.username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        to_user = models.User.get(models.User.username ** username)  #find the user
    except models.DoesNotExist:
        pass
    else:
        try:models.Relationship.get(  #if user exists create the relationship of from user and to user
            from_user =g.user._get_current_object(),
            to_user = to_user
        ).delete_instance()
        except models.IntegrityError:
            pass
        else:
            flash('You have unfollowed {}!'.format(to_user.username),'success')
    return redirect(url_for('stream', username=to_user.username))

@app.errorhandler(404)  #404 Decorator
def not_found(error):
    return render_template('404.html')

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