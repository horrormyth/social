from flask import render_template, flash, redirect, url_for, abort, g, Flask, app, Blueprint
from flask_bcrypt import check_password_hash
from flask_login import current_user, login_user, login_required, logout_user
from peewee import DoesNotExist, IntegrityError

import forms
from models import User, Post, Relationship

social = Blueprint('social', __name__)


@social.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        flash('Registration Succesful', 'success')
        User.create_users(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('social.index'))
    return render_template('register.html', form=form)


@social.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = User.get(User.email == form.email.data)
        except DoesNotExist:
            flash('Your email or Password doesnt match', 'error')
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)  # creating sessions on users browser and giving the cookie
                flash('You are logged in', 'success')
                return redirect(url_for('social.index'))
            else:
                flash('Your email or Password doesnt match', 'error')
    return render_template('login.html', form=form)


@social.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are Logged Out', 'success')
    return redirect(url_for('social.index'))


@social.route('/')
def index():
    stream_ = Post.select().limit(100)
    return render_template('stream.html', stream=stream_)


@social.route('/new_post', methods=('GET', 'POST'))
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        Post.create(user=g.user._get_current_object(),
                    content=form.content.data.strip())
        flash('Message Posted', 'success')
        return redirect(url_for('social.index'))
    return render_template('post.html', form=form)


@social.route('/stream')
@social.route('/stream/<username>')
@login_required
def stream(username=None):
    template = 'stream.html'
    if username and username != current_user.username:
        try:
            user = User.select().where(User.username ** username).get()
        except DoesNotExist:
            abort(404)
        else:
            stream = user.posts.limit(100)
    else:
        stream = current_user.get_stream().limit(100)
        user = current_user
    if username:
        template = 'user_stream.html'
    return render_template(template, stream=stream, user=user)


@social.route('/post/<int:post_id>')
def view_post(post_id):
    posts = Post.select().where(Post.id == post_id)
    if posts.count() == 0:
        abort(404)
    return render_template('stream.html', stream=posts)


@social.route('/follow/<username>')
@login_required
def follow(username):
    try:
        to_user = User.get(User.username ** username)
    except DoesNotExist:
        abort(404)
    else:
        try:
            Relationship.create(
                from_user=g.user._get_current_object(),
                to_user=to_user
            )
        except IntegrityError:
            pass
        else:
            flash('You are now following {}!'.format(to_user.username), 'success')
    return redirect(url_for('social.stream', username=to_user.username))


@social.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        to_user = User.get(User.username ** username)  # find the user
    except DoesNotExist:
        pass
    else:
        try:
            Relationship.get(
                from_user=g.user._get_current_object(),
                to_user=to_user
            ).delete_instance()
        except IntegrityError:
            pass
        else:
            flash('You have unfollowed {}!'.format(to_user.username), 'success')
    return redirect(url_for('social.stream', username=to_user.username))
