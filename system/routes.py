from system import app, forms, models, db, bcrypt, mail
from flask import render_template, url_for, flash, redirect, request, abort
import json, os, secrets
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

def save_picture(form_picture):
    random_hex = secrets.token_hex(10)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)
    
    return picture_fn

@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, int)
    posts = models.Post.query.order_by(models.Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html', title="About")

@app.route('/register', methods=['GET', 'POST'])
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
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)

@app.route('/login', methods=['GET', 'POST'])
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

@app.route('/logout')
def logout():
    logout_user()
    flash('Logged Out', 'success')
    return redirect('/')

@app.route('/account', methods=['GET', 'POST'])
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
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title="My Account", image_file=image_file, form=form)

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    form = forms.PostForm()
    if form.validate_on_submit():
        post = models.Post(title=form.title.data, content=form.content.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash("Post has been saved successfully.", "success")
        return redirect('/')
    return render_template('create_post.html', title="New Post", form=form, legend="New Post")

@app.route('/post/<int:post_id>')
def post(post_id):
    post = models.Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = models.Post.query.get_or_404(post_id)
    if current_user != post.author:
        abort(403)
    form = forms.PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Post updated succcessfully.", "success")
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', legend="Update Post", title="Update Post", form=form)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = models.Post.query.get_or_404(post_id)
    if current_user != post.author:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post has been deleted successfully.", "success")
    return redirect('/')

@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, int)
    user = models.User.query.filter_by(username=username).first_or_404()
    posts = models.Post\
        .query\
        .filter_by(author=user)\
        .order_by(models.Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

def send_reset_email(user):
    token = user.getToken()
    msg = Message("Password Reset Request", recipients=[user.email], sender="noreply@demo.com")
    msg.body = f''' Click on the following link to reset your password:
    { url_for('reset_validate', token=token, _external=True) }
    Kindly ignore this email if you didn't request this.
    '''
    mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect('/')
    form = forms.RequestResetForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with the reset instructions.", "info")
    return render_template('reset_password.html', form=form, title="Reset Password")

@app.route('/reset_password/<string:token>', methods=['GET', 'POST'])
def reset_validate(token):
    if current_user.is_authenticated:
        return redirect('/')
    form = forms.ResetPasswordForm()
    user = models.User.verifyToken(token)
    if user is None:
        flash("Token invalid or expired!", "danger")
        return redirect(url_for('reset_request'))
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You may now login.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_validate.html', form=form, title="Reset Password")