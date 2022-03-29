
import json
from urllib.request import Request
import flask
import flask_bcrypt as bcrypt
from datetime import datetime
from cerberus import Validator
from models import Devices, Opened, Users
from __main__ import app, login_manager, db
from flask import Response, render_template, request
from utility import LoginForm, VAPID_PUBLIC_KEY, send_web_push
from flask_login import current_user, login_required, login_user


api_keys = open("apikeys.txt", "r").read().split("\n")
devices = Devices.query.all()

renameValidator = Validator(
    {"name": {"type": "string", "maxlength": 50, "minlength": 1},
     "apikey": {"type": "string", "maxlength": 64, "minlength": 64}},
    require_all=True)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, user.salt + form.password.data):
                login_user(user)
            return flask.redirect(flask.url_for("index"))
    return render_template("login.html", form=form)


@app.route("/subscription/", methods=["GET", "POST", "DELETE"])
@login_required
def subscription():
    """
        POST creates a subscription
        GET returns vapid public key which clients uses to send around push notification
        DELETE removes subscription
    """

    if request.method == "GET":
        return Response(response=json.dumps({"public_key": VAPID_PUBLIC_KEY}),
                        headers={"Access-Control-Allow-Origin": "*"}, content_type="application/json")
    if request.method == "DELETE":
        current_user.token = None
        db.session.commit()
        return Response(status=200)

    current_user.token = request.form["subscription_token"]
    db.session.commit()
    return Response(status=201, mimetype="application/json")


@app.route("/api/sensor", methods=["GET"])
def boardAPI():
    api_key = request.args.get("api_key")
    # TODO Validate via validate
    if api_key and api_key in api_keys:
        command = request.args.get("command")
        if command == "alive":
            missing = True
            for device in devices:
                if device["apikey"] == api_key:
                    device["lastSignal"] = datetime.now()
                    missing = False
            if missing:
                new_Device = Devices()
                new_Device.apikey = api_key
                db.session.add(new_Device)
                db.session.commit()
        elif command == "alert":
            for user in Users.query.all():
                send_web_push(json.loads(user.token), user.username)
                new_openend = Opened()
                new_openend.time = datetime.now()
                for device in devices:
                    if device.apikey == api_key:
                        new_openend.device = device
                db.session.add(new_openend)
                db.seccion.commit()
        return Response(status=200)
    return Response(status=403)


@app.route("/api/data", methods=["GET", "POST"])
@login_required
def dataAPI():
    if request.method == "GET":
        # FIXME
        return Response(json.dumps(
            {"devices": [device.toJSON() for device in devices], "opened": [opened.toJSON() for opened in db.session.query(Opened).limit(5)]}), content_type="application/json", status=200)
    if not request.json:
        return Response(status=400)
    data = request.json
    if renameValidator.validate(data):
        if not data["apikey"] in api_keys:
            return Response("Apikey not found", status=404)
        for device in devices:
            if device.apikey == data["apikey"]:
                device.name = data["name"]
                db.session.commit()
        return Response(status=200)
    return Response(json.dumps(renameValidator.errors), status=400)
