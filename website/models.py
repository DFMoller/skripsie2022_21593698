from . import db
from flask_login import UserMixin

# Usage includes a row every 30 min, containing the accumulated usage for the last 30 min period
class Usage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.String(100))
    usage = db.Column(db.Integer) # Consider changing this to float (db.Float)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))

# Demand includes a row every 30 min, containing the highest instantaneos power pulled in the last 30 min
class Peak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.String(100))
    peak = db.Column(db.Integer) # Consider changing this to float
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))

class Client(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    hash = db.Column(db.String(100))
    usages = db.relationship('Usage')
    peaks = db.relationship('Peak')