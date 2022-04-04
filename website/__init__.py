# from typing_extensions import Required
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from os import path
import json, jwt
from jwt import InvalidSignatureError
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()
DB_NAME = "power_database.db"
app = Flask(__name__)

def create_app():

    app.config['SECRET_KEY'] = 'abcdefg' # secures cookies and session data
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    db.init_app(app)

    # Register blueprints
    from .views import views

    # Register all views
    app.register_blueprint(views, url_prefix='/') # prefix would go before any routes in blueprints

    # Make sure this model file runs befor we initialize our Database
    from .models import Usage, Peak, Client

    # Check if db exists, else create new
    create_database(app)

    # Register Admin Views
    admin = Admin(app)
    admin.add_view(ModelView(Usage, db.session))
    admin.add_view(ModelView(Peak, db.session))
    admin.add_view(ModelView(Client, db.session))

    # Define all possible api calls
    startRestfulAPI(app, Usage, Peak)

    # Setup Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'views.login'
    login_manager.login_message = 'Please log in first!'
    login_manager.login_message_category = 'flash_error flash'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Client.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Database Created!')
    else:
        print('Database Found!')

def startRestfulAPI(app, Usage, Peak):
    
    api = Api(app)

    post_usage_args = reqparse.RequestParser()
    post_usage_args.add_argument("datetime", type=str, help="Date and time at the end of interval required as a string...", required=True)
    post_usage_args.add_argument("usage", type=int, help="Usage (Wh) required as an integer...", required=True)
    post_usage_args.add_argument("api_key", type=str, help="API key required...", required=True)

    post_peak_args = reqparse.RequestParser()
    post_peak_args.add_argument("datetime", type=str, help="Date and time at the end of interval required as a string...", required=True)
    post_peak_args.add_argument("peak", type=int, help="Peak demand (W) required as an integer...", required=True)
    post_peak_args.add_argument("api_key", type=str, help="API key required...", required=True)

    usage_fields = {
        "id": fields.Integer,
        "datetime": fields.String,
        "usage": fields.Integer,
        "api_key": fields.String
    }

    peak_fields = {
        "id": fields.Integer,
        "datetime": fields.String,
        "peak": fields.Integer,
        "api_key": fields.String
    }

    class postUsage(Resource):

        # @marshal_with(usage_fields)
        def post(self):

            args = post_usage_args.parse_args()
            feedback = {}

            print(f'USAGE:\n\tdatetime: {args["datetime"]}\n\tusage: {str(args["usage"])}\n\tAPI_KEY: {args["api_key"]}')

            try:
                decoded = jwt.decode(args['api_key'], app.config['SECRET_KEY'], algorithms=["HS256"])
                new_usage = Usage(datetime=args['datetime'], usage=args['usage'], client_id=decoded['id'])
                db.session.add(new_usage)
                db.session.commit()
                feedback["message"] = "Usage data received and saved"
            except InvalidSignatureError:
                feedback["message"] = "Invalid API Key"
                return feedback, 401

            return feedback
    
    class postPeak(Resource):

        # @marshal_with(peak_fields)
        def post(self):

            args = post_peak_args.parse_args()
            feedback = {}

            print(f'PEAK:\n\tdatetime: {args["datetime"]}\n\tpeak: {str(args["peak"])}\n\tAPI_KEY: {args["api_key"]}')

            try:
                decoded = jwt.decode(args['api_key'], app.config['SECRET_KEY'], algorithms=["HS256"])
                new_peak = Peak(datetime=args['datetime'], peak=args['peak'], client_id=decoded['id'])
                db.session.add(new_peak)
                db.session.commit()
                feedback["message"] = "Peak data received and saved"
            except InvalidSignatureError:
                feedback["message"] = "Invalid API Key"
                return feedback, 401

            return feedback
    
    api.add_resource(postUsage, "/postUsage")
    api.add_resource(postPeak, "/postPeak")

def generate_api_key(id, email):
    new_key = jwt.encode({"id": id, "email": email}, app.config['SECRET_KEY'], algorithm="HS256")
    return new_key
