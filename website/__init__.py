# from typing_extensions import Required
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from os import path
import json

db = SQLAlchemy()
DB_NAME = "power_database.db"

def create_app():

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'abcdefg' # secures cookies and session data
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SECRET_KEY'] = 'abcdefg' # secures cookies and session data

    db.init_app(app)

    # Register blueprints
    from .views import views

    # Register all views
    app.register_blueprint(views, url_prefix='/') # prefix would go before any routes in blueprints

    # Make sure this model file runs befor we initialize our Database
    from .models import Usage, Peak

    # Check if db exists, else create new
    create_database(app)

    # Define all possible api calls
    startRestfulAPI(app)

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Database Created!')
    else:
        print('Database Found!')

def startRestfulAPI(app):
    
    api = Api(app)

    post_usage_args = reqparse.RequestParser()
    post_usage_args.add_argument("datetime", type=str, help="Date and time at the end of interval required as a string...", required=True)
    post_usage_args.add_argument("usage", type=int, help="Usage (Wh) required as an integer...", required=True)

    post_peak_args = reqparse.RequestParser()
    post_peak_args.add_argument("datetime", type=str, help="Date and time at the end of interval required as a string...", required=True)
    post_peak_args.add_argument("peak", type=int, help="Peak demand (W) required as an integer...", required=True)

    usage_fields = {
        "id": fields.Integer,
        "datetime": fields.String,
        "usage": fields.Integer
    }

    peak_fields = {
        "id": fields.Integer,
        "datetime": fields.String,
        "peak": fields.Integer
    }

    class postUsage(Resource):

        @marshal_with(usage_fields)
        def post(self):

            args = post_usage_args.parse_args()

            print(f'USAGE:\n\tdatetime: {args["datetime"]}\n\tusage: {str(args["usage"])}')

            feedback = {
                "message": "Usage Received"
            }

            return feedback
    
    class postPeak(Resource):

        @marshal_with(peak_fields)
        def post(self):

            args = post_peak_args.parse_args()

            print(f'USAGE:\n\tdatetime: {args["datetime"]}\n\tpeak: {str(args["peak"])}')

            feedback = {
                "message": "Peak Received"
            }

            return feedback
    
    api.add_resource(postUsage, "/postUsage")
    api.add_resource(postPeak, "/postPeak")

