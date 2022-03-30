from . import db

# Usage includes a row every 30 min, containing the accumulated usage for the last 30 min period
class Usage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(100))
    usage = db.Column(db.Integer) # Consider changing this to float (db.Float)

# Demand includes a row every 30 min, containing the highest instantaneos power pulled in the last 30 min
class Peak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(100))
    peak = db.Column(db.Integer) # Consider changing this to float

