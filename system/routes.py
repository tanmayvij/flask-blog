from system import app, forms, models
from flask import render_template, url_for, flash, redirect
import json

with open('posts.json') as json_set:
    posts = json.load(json_set)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html', title="About")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for { form.username.data }!", category="success")
        return redirect('/')
    return render_template('register.html', title="Register", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        if form.email.data == "test@example.com" and form.password.data == "hello":
            flash('You have been logged in!', 'success')
            return redirect('/')
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title="Login", form=form)