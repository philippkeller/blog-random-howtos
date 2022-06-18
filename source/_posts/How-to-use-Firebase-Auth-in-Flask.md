---
title: How to use Firebase Auth in Flask
date: 2022-06-16 21:06:34
tags:
---

Using Firebase auth in Flask is currently under-documented on the web. I spent hours scraping together the relevant information which, I hope, I can present here in a good form - in order to improve the world and achieve world peace!

<!-- more -->

## How would do firebase and flask work together?

The easiest way to use Firebase is to use [FirebaseUI](https://firebase.google.com/docs/auth/web/firebaseui). This is a javascript library which renders the social login buttons, handles account linking, supports one tab sign-in, localized ui, basically all things you would expect from an authentication provider (unlike Cognito, you stinker!).

You can use [this demo](https://fir-ui-demo-84a6c.firebaseapp.com/) to get a feel of what FirebaseUI provides.

### How and when do you include FirebaseUI into your flask templates?

I was confused about this at first. I thought that FirebaseUI holds some sort of "authentication token" and would redirect if the login expires etc. This is not the case.

FirebaseUI has no idea if your user is logged in or not. It is just used to trigger the flow.

Additionally: the login and registration flow is the same. It creates a user if necessary. That also simplifies things.

### How does FirebaseUI call flask?

FirebaseUI offers the callback [signInSuccess](https://firebase.google.com/docs/auth/web/firebaseui#sign_in) in which you do an ajax request to flask to trigger the login

In flask you receive the ajax request token. Since the javascript client is untrusted (basically everyone can call your flask api) you need to [validate the token](https://firebase.google.com/docs/auth/admin/verify-id-tokens#python) either using [pyrebase](https://github.com/thisbejim/Pyrebase) or [pyjwt](https://github.com/jpadilla/pyjwt)

### Where is the user information stored? It's all in firebase, right? So I would not store it in my database?

I was confused about this, because I thought, that all user related data would be stored in firebase, but usually you want to store some additional things like name or profile picture. Firebase only stores email and the userid so any additional data you would need to store in your custom database.

Also, Firebase is only handling authentication, not authorization. So if you want to have a group of users able to access an admin area, then you need to store it outside firebase.

The validated token you get handed over by signInSuccess contains email, name, etc. (what you get back from a regular OAuth2 flow, depends on the social login provider, e.g. facebook doesn't always provide email!) and additionally the firebase userid. So you need a table in your database to store these things, which you'd want to use in your flask templates e.g. to greet the user by name.

### How does this work with flask_login?

If you're using [flask-login](https://flask-login.readthedocs.io/en/latest/) (and I guess most people do), then you need to hook it into the following places:

- [login_manager.unauthorized_handler](https://flask-login.readthedocs.io/en/latest/#flask_login.LoginManager.unauthorized_handler): this is called when you a flask view has `@login_required` and a user is not logged in yet. You'd want to redirect to the flask templates which includes FirebasUI
- [login_user(account)](https://flask-login.readthedocs.io/en/latest/#flask_login.login_user): you call this when you got the callback signInSuccess from FirebaseUI. This puts the user into "logged in" state and stores it into the Flask session (stored on client side)
- [login_manager.user_loader](https://flask-login.readthedocs.io/en/latest/#flask_login.LoginManager.user_loader): this is called for every `@login_required` to check if the user is logged in and to load user data into the [current user](https://flask-login.readthedocs.io/en/latest/#flask_login.current_user) variable

## I don't want to write all this boilerplate code

Right. Me neither. Luckily there's [flask-firebase](https://github.com/klokantech/flask-firebase) which handles all the above. The documentation is a bit lacking so here's a howto to get this working (I issued a [pull request](https://github.com/klokantech/flask-firebase/pull/6) to fix it, but that got not accepted yet):

**Before you start:**

You need the following infos before you start:

- `FIREBASE_API_KEY`: The API key. Get this from Firebase -> Project settings -> web api key
- `FIREBASE_PROJECT_ID`: The project identifier, eg. foobar. Project settings -> Project ID
- `FIREBASE_AUTH_SIGN_IN_OPTIONS`: Comma-separated list of enabled providers. Possible providers are email, facebook, github, google and twitter

And then you need…

- to ensure you have sqlite installed
- pip install the following packages into your virtualenv: flask, requests, flask_login, flask_sqlalchemy and pyjwt
- allow self-signed certificate on localhost: in chrome go to chrome://flags/#allow-insecure-localhost and enable the setting

Now, git clone `git@github.com:klokantech/flask-firebase.git` into a directory (sadly it's not provided via pypi yet) and in that same directory put the following code into `app.py` (replace all REPLACE_ME with the needed info)

```python
from flask import Flask, request, redirect
from flask_firebase import FirebaseAuth
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.debug = False # to disable local testing
app.config['FIREBASE_API_KEY'] = 'REPLACE_ME'
app.config['FIREBASE_PROJECT_ID'] = 'REPLACE_ME'
app.config['FIREBASE_AUTH_SIGN_IN_OPTIONS'] = 'google,facebook' # <-- coma separated list, see Providers above
app.config['SECRET_KEY'] = 'REPLACE_ME' # <-- random string
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/firebase_users.db'

db = SQLAlchemy(app)
auth = FirebaseAuth(app)
login_manager = LoginManager(app)

app.register_blueprint(auth.blueprint, url_prefix='/auth')


class Account(UserMixin, db.Model):

    __tablename__ = 'accounts'

    account_id = db.Column(db.Integer)
    firebase_user_id = db.Column(db.Text, unique=True, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    name = db.Column(db.Text)
    photo_url = db.Column(db.Text)
    
    def get_id(self):
        return self.firebase_user_id

    def __repr__(self):
        return str(dict(firebase_user_id=self.firebase_user_id, email=self.email, name=self.name))


db.create_all() # <-- don't use this in production! This creates the account table in your sqlite
db.session.commit()

@auth.production_loader
def production_sign_in(token):
    account = Account.query.filter_by(firebase_user_id=token['sub']).one_or_none()
    if account is None:
        account = Account(firebase_user_id=token['sub'])
        db.session.add(account)
    account.email = token['email']
    account.email_verified = token['email_verified']
    account.name = token.get('name')
    account.photo_url = token.get('picture')
    db.session.flush()
    login_user(account)
    db.session.commit()


@auth.development_loader
def development_sign_in(email):
    login_user(Account.query.filter_by(email=email).one())

@auth.unloader
def sign_out():
    logout_user()

@login_manager.user_loader
def load_user(account_id):
    return Account.query.get(account_id)

@login_manager.unauthorized_handler
def authentication_required():
    return redirect(auth.url_for('widget', mode='select', next=request.url))

@app.route("/")
@login_required
def index():
    return f"<p>Hello, {current_user.name}!</p>"
```

Now, you need to run the server with SSL enabled, otherwise the social login providers would not allow the sign-in. 

Therefore start the server with `export FLASK_DEBUG=1 && venv/bin/flask run --with-threads --cert adhoc`
If all goes well then you get redirected to the login flow and are then greeted in the index() view with your name.

## Use it in production

The code is pretty much production ready. Of course you'd want to use a different sqlalchemy database, and get rid of db.create_all() and db.session.commit()

You might want to style that login page a bit, for this, create a new template in `templates/firebase_auth/widget.html` and do something like this:

```
{% extends "firebase_auth/widget_base.html" %}

{% block scripts %}
<!-- include your js files here -->
{% endblock %}

{% block styles %}
<style>
    body {
      margin: auto;
      padding: auto;
      text-align: center;
    }
</style>
{% endblock %}

{% block header %}
<!-- include your header/navigation/… here -->
{% endblock %}

{% block footer %}
<!-- include your footer here -->
{% endblock %}

```

