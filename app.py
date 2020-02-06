from flask import Flask, render_template, url_for, flash, redirect
app = Flask(__name__)
import json, forms
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.flask_blog

app.config['SECRET_KEY'] = '959d21577205efa16538037a'

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
        newUser = {
            "username": form.username.data,
            "email": form.email.data,
            "password": form.password.data
        }
        db.users.insert_one(newUser)
        flash(f"Account created for { form.username.data }!", category="success")
        return redirect('/')
    return render_template('register.html', title="Register", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():

        user = db.users.find_one({"email": form.email.data})
        if not user:
            flash("User does not exist", "danger")
        elif form.password.data == user['password']:
            flash('You have been logged in!', 'success')
            return redirect('/')
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title="Login", form=form)

if __name__ == '__main__':
    app.run()