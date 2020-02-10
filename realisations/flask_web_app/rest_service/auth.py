from flask import Blueprint, request
from flask_login import login_user

from .database import db
from .models import User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['POST'])
def login():
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(name=name).first()
    if user.pswd == password:
        login_user(user, remember=True)
    else:
        return 'fail'

    return 'Login'


@auth.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    password = request.form.get('password')
    user = User.query.filter_by(
        name=name).first()  # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        return ('already exist')

    new_user = User(name=name, pswd=password)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return 'Created user'


@auth.route('/logout')
def logout():
    return 'Logout'