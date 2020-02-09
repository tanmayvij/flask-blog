from flask import render_template, url_for, redirect, request, flash, Blueprint
from system.users import forms
from system import db, bcrypt, models
from flask_login import login_required, login_user, logout_user, current_user
from system.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect('/')
    
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        pwdHash = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = models.User(username=form.username.data, password=pwdHash, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        flash(f"Account created for { form.username.data }! You can now login.", category="success")
        return redirect(url_for('users.login'))
    return render_template('register.html', title="Register", form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        if not user:
            flash("This email address does not exist.", "danger")
        elif not bcrypt.check_password_hash(user.password, form.password.data):
            flash("Invalid password. Please try again", "danger")
        else:
            login_user(user, remember=form.remember.data)
            flash('You have been logged in!', 'success')
            next = request.args.get('next')
            return redirect(next) if next else redirect('/')
    return render_template('login.html', title="Login", form=form)

@users.route('/logout')
def logout():
    logout_user()
    flash('Logged Out', 'success')
    return redirect('/')

@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    form = forms.UpdateForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title="My Account", image_file=image_file, form=form)

@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, int)
    user = models.User.query.filter_by(username=username).first_or_404()
    posts = models.Post\
        .query\
        .filter_by(author=user)\
        .order_by(models.Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect('/')
    form = forms.RequestResetForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with the reset instructions.", "info")
    return render_template('reset_password.html', form=form, title="Reset Password")

@users.route('/reset_password/<string:token>', methods=['GET', 'POST'])
def reset_validate(token):
    if current_user.is_authenticated:
        return redirect('/')
    form = forms.ResetPasswordForm()
    user = models.User.verifyToken(token)
    if user is None:
        flash("Token invalid or expired!", "danger")
        return redirect(url_for('users.reset_request'))
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You may now login.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_validate.html', form=form, title="Reset Password")
