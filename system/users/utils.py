import os, secrets
from flask_mail import Message
from system import mail
from flask import url_for, current_app

def save_picture(form_picture):
    random_hex = secrets.token_hex(10)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)
    
    return picture_fn

def send_reset_email(user):
    token = user.getToken()
    msg = Message("Password Reset Request", recipients=[user.email], sender="noreply@demo.com")
    msg.body = f''' Click on the following link to reset your password:
    { url_for('users.reset_validate', token=token, _external=True) }
    Kindly ignore this email if you didn't request this.
    '''
    mail.send(msg)