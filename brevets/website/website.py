import flask
from flask import Flask, session, request, Response, render_template, redirect, url_for, flash, abort
import requests
import os
from urllib.parse import urlparse, urljoin
from passlib.apps import custom_app_context as pwd_context
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user, UserMixin,
                         confirm_login, fresh_login_required)
from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, StringField, validators
import json


app = Flask(__name__)

app.secret_key = os.urandom(24)

app.config.from_object(__name__)

login_manager = LoginManager()

login_manager.session_protection = "strong"

login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."

login_manager.refresh_view = "login"
login_manager.needs_refresh_message = (
    u"To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"
login_manager.init_app(app)

API_URL = 'http://{}:{}'.format(os.environ['RESTAPI_HOSTNAME'], os.environ['RESTAPI_PORT'])


class LoginForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25, message='Username must be between 2 and 25 characters'),
        validators.InputRequired(u'Username required')
    ])
    password = StringField('Password', [
        validators.Length(min=2, max=25, message='Password must be between 2 and 25 characters'),
        validators.InputRequired(u'Password required')
    ])
    remember = BooleanField('Remember me')


class RegisterForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25, message='Username must be between 2 and 25 characters'),
        validators.InputRequired(u'Username required')
    ])
    password = StringField('Password', [
        validators.Length(min=2, max=25, message='Password must be between 2 and 25 characters'),
        validators.InputRequired(u'Password required')
    ])


class User(UserMixin):
    def __init__(self, username, token):
        self.username = username
        self.token = token


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@login_manager.user_loader
def load_user(user_id):
    username = session['username']
    if username is None:
        return None
    user = User(username, flask.session.get('token'))
    return user


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/_req')
def req():
    token = session.get("token")
    format = flask.request.args.get('format', default='json', type=str)
    k = flask.request.args.get('k', default=0, type=int)
    open = flask.request.args.get('check_open', default='', type=str)
    close = flask.request.args.get('check_close', default='', type=str)
    if open and close:
        option = 'listAll'
    elif open:
        option = 'listOpenOnly'
    else:
        option = 'listCloseOnly'
    url = API_URL + '/' + option + '/' + format + '?top=' + str(k) + "&" + token
    r = requests.get(url)
    return r.text


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit() and request.method == "POST":
      username = request.form['username']
      password = request.form['password']
      if username is None or password is None:
        return Response('Username or password missing', 400)
      resp = requests.post(API_URL + '/register', params={'username': username, 'password': password})
      if resp.status_code == 201:
        flash("Registration complete")
      else:
        flash("Registration failure")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit() and request.method == "POST" and "username" in request.form:
        username = request.form["username"]
        password = request.form["password"]
        remember = request.form.get("remember", "false") == "true"
        resp = requests.get(API_URL + '/token', params={'username': username, 'password': password})
        if resp.status_code == 200:
            user_data = json.loads(resp.text)
            token = user_data.get('token')
            user = User(username, token)
            if login_user(user, remember=remember):
                session['username'] = username
                session['token'] = token
                flash("Logged in!")
                flash("I'll remember you") if remember else None
                next = request.args.get("next")
                if not is_safe_url(next):
                    abort(400)
                return redirect(next or url_for('index'))
            else:
                flash("Sorry, but you could not log in.")
        else:
            flash(u"Invalid username or password.")
    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
