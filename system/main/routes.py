from flask import render_template, request, Blueprint
from system import models

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', 1, int)
    posts = models.Post.query.order_by(models.Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)

@main.route('/about')
def about():
    return render_template('about.html', title="About")
