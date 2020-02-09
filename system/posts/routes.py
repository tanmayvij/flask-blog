from flask import render_template, url_for, flash, redirect, abort, request, Blueprint
from flask_login import current_user, login_required
from system import db, models
from system.posts import forms

posts = Blueprint('posts', __name__)

@posts.route('/post/new', methods=['GET', 'POST'])
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

@posts.route('/post/<int:post_id>')
def post(post_id):
    post = models.Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
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
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', legend="Update Post", title="Update Post", form=form)

@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = models.Post.query.get_or_404(post_id)
    if current_user != post.author:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post has been deleted successfully.", "success")
    return redirect('/')