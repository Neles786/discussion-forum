from flask import render_template, url_for, flash, redirect, request, Blueprint
from discussions import db, bcrypt
from discussions.appusers.forms import SignupForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from discussions.models import Users, Post
from flask_login import login_user, current_user, logout_user, login_required
from discussions.appusers.utils import save_picture, send_reset_email

appusers = Blueprint('appusers', __name__)

@appusers.route("/signup", methods=['GET','POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user = Users(
                     username = form.username.data, 
                     password = hashed_password, 
                     email = form.email.data, 
                     mobileno = form.mobileno.data
                     )
        db.session.add(user)
        db.session.commit()
        flash(f'Your Account has been created! You are now able to login', 'success')
        return redirect(url_for('main.home'))
    return render_template('signup.html',form=form)

@appusers.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful, please check your email and password', 'danger')
    return render_template('login.html',form=form)

@appusers.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@appusers.route("/account", methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            current_user.image_file = save_picture(form.picture.data)
        # current_user.name = form.name.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.mobileno = form.mobileno.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('appusers.account'))
    elif request.method == 'GET':
        # form.name.data = current_user.name
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.mobileno.data = current_user.mobileno
    image_file = url_for('static', filename='profile_pics/'+ current_user.image_file)
    return render_template('account.html', image_file=image_file, form=form)

@appusers.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page',1,type=int)
    user = Users.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(per_page=2,page=page)
    return render_template('user_posts.html', posts=posts, user=user)

@appusers.route("/reset_password", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('appusers.login'))
    return render_template('reset_request.html', form=form)

@appusers.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = Users.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('appusers.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('appusers.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)