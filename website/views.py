from sqlalchemy import false
from . import db, generate_api_key
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from .models import Client, Data
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import datetime, json
from .plotting import prepare_chart_data
from enum import Enum
from .quotation import Quotation
from .analysis import Analysis

views = Blueprint('views', __name__) # don't have to call it the file name

# class Period(Enum):
#     p24h = 1
#     p72h = 2
#     p1w = 3

@views.route('/', methods=["GET", "POST"])
@login_required
def home():

    data_entries = Data.query.filter_by(client_id=current_user.id)

    key = ""
    if request.method == "GET":
        key = "24h"
    elif request.method == "POST":
        key = request.form.get("period-selection")

    hours = 0
    if key == "24h": hours = 24
    elif key == "72h": hours = 72
    elif key == "week": hours = 168

    usage_values, peak_values, xlabels = prepare_chart_data(data_entries, key)

    today = str(datetime.datetime.today().date())
    
    return render_template("home.html", user=current_user, xlabels=xlabels, usage_values=usage_values, peak_values=peak_values, date=today, hours=hours)

@views.route('/csv', methods=['GET'])
@login_required
def csv():
    datapoints = Data.query.filter_by(client_id=current_user.id)
    csv = 'datetime,usage,peak\n'
    for dp in datapoints:
        csv += f'{dp.datetime},{dp.usage},{dp.peak}'
        csv += '\n'
        response = make_response(csv)
    cd = 'attachment; filename=measurements.csv'
    response.headers['Content-Disposition'] = cd
    response.mimetype='text/csv'
    return response


@views.route('/analysis', methods=['GET', 'POST'])
@login_required
def analysis():
    if request.method == 'POST':
        usage_str  = request.form.get('usage_values').strip('][').split(', ')
        peak_str = request.form.get('peak_values').strip('][').split(', ')
        # data from load profile
        aggregated_data = {
            'usage': [int(val) for val in usage_str],
            'peak': [int(val) for val in peak_str]
        }
        pwrHours = int(request.form.get('pwrHours'))
        chargeHours = float(request.form.get('chargeHours'))
        Quote1 = Quotation(batV=48, powerHours=pwrHours, chargingHours=chargeHours, usage_mode='median', peak_mode='maximum', aggregated_data=aggregated_data)
        return json.dumps(Quote1.quotation_results)
    else:
        datapoints = Data.query.filter_by(client_id=current_user.id)
        Analysis1 = Analysis(datapoints)
        # Quote1 = Quotation(batV=24, powerHours=8, chargingHours=5, datapoints=datapoints, usage_mode='median', peak_mode='median')
        return render_template("analysis.html", xlabels=Analysis1.aggregated_data['xlabels'], usage_values=Analysis1.aggregated_data['usage'], peak_values=Analysis1.aggregated_data['peak'])

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