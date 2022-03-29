import json
from __main__ import db
from sqlalchemy import orm, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from flask_login import UserMixin


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    salt = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    token = db.Column(db.String(20), nullable=True)


class Devices(db.Model):
    __tablename__ = 'devices'
    apikey = db.Column(db.String(64), primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=True)
    entrys = relationship("Opened", backref="device")

    def __init__(self) -> None:
        super().__init__()
        self.lastSignal = datetime.now()

    @orm.reconstructor
    def init_on_load(self):
        self.lastSignal = None

    def toJSON(self):
        return json.dumps({"apikey": self.apikey, "name": self.name, "lastSignal": self.lastSignal})


class Opened(db.Model):
    __tablename__ = 'opened'
    time = db.Column(db.DateTime, primary_key=True)
    devicekey = db.Column(db.String(64), ForeignKey(
        "devices.apikey"), primary_key=True)

    def toJSON(self):
        return json.dumps({"time": self.time.strftime("%d/%m/%Y, %H:%M:%S"), "device": self.device.toJSON()})
