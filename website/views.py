from . import db
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Client
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

views = Blueprint('views', __name__) # don't have to call it the file name

@views.route('/', methods=["GET", "POST"])
def home():
    # flash("Testing", "flash_success")
    return render_template("home.html")

@views.route('/signup', methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        # Form has been submitted
        email = request.form.get("email")
        pwd1 = request.form.get("pwd1")
        pwd2 = request.form.get("pwd2")

        print("Test1")

        client = Client.query.filter_by(email=email).first()

        if len(email) < 4:
            flash("Email must be longer than 3 characters!", "flash_error flash")
        elif client:
            flash("A Client with that email already exists!", "flash_error flash")
        elif pwd1 != pwd2:
            flash("Passwords do not match!", "flash_error flash")
        elif len(pwd1) < 7:
            flash("Password must be at least 7 characters long!")
        else:
            print("Pass")
            new_client = Client(email=email, hash=generate_password_hash(pwd1, method='sha256'))
            db.session.add(new_client)
            db.session.commit()
            login_user(new_client, remember=True)
            flash("Account Created!", "flash_success flash")

            return redirect(url_for('views.home'))

    return render_template("signup.html")

@views.route('/login', methods=["GET", "POST"])
def login():

    if request.method == "POST":
        
        email = request.form.get("email")
        pwd = request.form.get("pwd")

        client = Client.query.filter_by(email=email).first()

        if not client:
            flash("No Client is registered with that email!", "flash_error flash")
        elif not check_password_hash(client.hash, pwd):
            flash("Incorrect Password!", category="flash_error flash")
        else:
            flash("Login Successful!", "flash_success flash")
            return redirect(url_for('views.home'))

    return render_template("login.html")

@views.route('/logout')
def logout():
    logout_user()
    flash("User logged out!", "flash_success flash")
    return redirect(url_for('views.login'))