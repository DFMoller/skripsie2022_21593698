from flask import Blueprint, render_template, request, redirect, url_for, flash

views = Blueprint('views', __name__) # don't have to call it the file name

@views.route('/', methods=["GET", "POST"])
def home():
    # flash("Testing", "flash_success")
    return render_template("home.html")