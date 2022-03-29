from __main__ import db
from datetime import datetime
from flask_login import UserMixin


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    salt = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    token = db.Column(db.String(20), nullable=True)


class Devices(db.Model):

    apikey = db.Column(db.String(64), primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=True)

    def __init__(self) -> None:
        super().__init__()
        self.lastSignal = datetime.now()


class Opened(db.Model):
    time = db.Column(db.DateTime, primary_key=False)
    device = db.Column(db.String(64), db.ForeignKey(
        'Device.apikey'), primary_key=True)
