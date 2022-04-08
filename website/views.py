from . import db, generate_api_key
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Client, Usage, Peak
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

views = Blueprint('views', __name__) # don't have to call it the file name

@views.route('/', methods=["GET", "POST"])
@login_required
def home():
    # This page will contain all data specific to the user
    usage_entries = Usage.query.filter_by(client_id=current_user.id)
    peak_entries = Peak.query.filter_by(client_id=current_user.id)
    return render_template("home.html", user=current_user, usage=usage_entries, peak=peak_entries)

@views.route('/signup', methods=["GET", "POST"])
def signup():

    email = ""
    pwd1 = ""
    pwd2 = ""

    if current_user.is_authenticated:
        flash("Please Sign out first before signing up a new user!", "flash_error flash")
        return redirect(url_for('views.home'))

    elif request.method == "POST":
        # Form has been submitted

        email = request.form.get("email")
        pwd1 = request.form.get("pwd1")
        pwd2 = request.form.get("pwd2")

        client = Client.query.filter_by(email=email).first()

        if len(email) < 4:
            flash("Email must be longer than 3 characters!", "flash_error flash")
        elif client:
            flash("A User with that email already exists!", "flash_error flash")
        elif pwd1 != pwd2:
            flash("Passwords do not match!", "flash_error flash")
        elif len(pwd1) < 7:
            flash("Password must be at least 7 characters long!", "flash_error flash")
        else:
            new_client = Client(email=email, hash=generate_password_hash(pwd1, method='sha256'))
            db.session.add(new_client)
            db.session.commit()
            login_user(new_client, remember=True)
            flash("Account Created!", "flash_success flash")

            return redirect(url_for('views.home'))

    return render_template("signup.html", email=email, pwd1=pwd1, pwd2=pwd2)

@views.route('/login', methods=["GET", "POST"])
def login():

    email = ""
    pwd = ""

    if request.method == "POST":
        
        email = request.form.get("email")
        pwd = request.form.get("pwd")

        client = Client.query.filter_by(email=email).first()

        if not client:
            flash("No User is registered with that email!", "flash_error flash")
        elif not check_password_hash(client.hash, pwd):
            flash("Incorrect Password!", category="flash_error flash")
        else:
            login_user(client, remember=True)
            flash("Login Successful!", "flash_success flash")
            return redirect(url_for('views.home'))

    return render_template("login.html", email=email, pwd=pwd)

@views.route('/logout')
def logout():
    logout_user()
    flash("User logged out!", "flash_success flash")
    return redirect(url_for('views.login'))

@views.route('/auth', methods=["GET", "POST"])
@login_required
def auth():

    api_key = generate_api_key(current_user.id, current_user.email)

    return render_template("auth.html", api_key=api_key, email=current_user.email)