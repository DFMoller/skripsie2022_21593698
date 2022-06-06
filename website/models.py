from . import db
from flask_login import UserMixin



class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.String(100))
    usage = db.Column(db.Integer) # Consider changing this to float (db.Float)
    peak = db.Column(db.Integer) # Consider changing this to float
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))

class Client(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    hash = db.Column(db.String(100))
    data_entries = db.relationship('Data')