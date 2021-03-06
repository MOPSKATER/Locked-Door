import json
import flask
from sqlalchemy import desc
import flask_bcrypt as bcrypt
from datetime import datetime
from cerberus import Validator
from models import Devices, Opened, Users
from main import app, login_manager, db
from flask import Response, render_template, request
from utility import LoginForm, VAPID_PUBLIC_KEY, send_web_push
from flask_login import current_user, login_required, login_user


api_keys = open("apikeys.txt", "r").read().split("\n")
devices = Devices.query.all()

renameValidator = Validator(
    {"name": {"type": "string", "maxlength": 50, "minlength": 1},
     "apikey": {"type": "string", "maxlength": 64, "minlength": 64}},
    require_all=True)

sensorAPIValidator = Validator(
    {
        "api_key": {"type": "string", "maxlength": 64, "minlength": 64},
        "command": {"type": "string", "allowed": ["alive", "alert"]}
    },
    reqire_all=True
)


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
            if bcrypt.check_password_hash(user.password, form.password.data):
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
    x = current_user.token
    return Response(status=201)


@app.route("/api/sensor", methods=["GET"])
def boardAPI():
    if not sensorAPIValidator.validate(request.args):
        return Response(json.dumps(sensorAPIValidator.errors), status=400)
    api_key = request.args.get("api_key")
    command = request.args.get("command")
    if api_key in api_keys:
        global devices
        if command == "alive" or command == "alert":
            missing = True
            for device in devices:
                if device.apikey == api_key:
                    device.lastSignal = datetime.now()
                    missing = False
            if missing:
                new_Device = Devices()
                new_Device.apikey = api_key
                db.session.add(new_Device)
                db.session.commit()
                devices = Devices.query.all()
        if command == "alert":
            new_openend = Opened()
            new_openend.time = datetime.now()
            for device in devices:
                if device.apikey == api_key:
                    new_openend.devicekey = device.apikey
                    new_openend.devicename = None if device.name == None else device.name
                    break
            db.session.add(new_openend)
            db.session.commit()
            for user in Users.query.all():
                if user.token != None:
                    try:
                        send_web_push(
                            json.loads(user.token),
                            json.dumps({
                                "name": "Unbenannt" if device.name == None else device.name,
                                "time": "Zeitstempel error" if new_openend.time == None else new_openend.time.strftime("%d/%m/%Y %H:%M:%S")
                            }))
                    except Exception as e:
                        print("error", e)
        return Response(status=200)
    return Response("Wrong api key", status=403)


@app.route("/api/data", methods=["POST"])
def post_dataAPI():
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


@app.route("/api/data", methods=["GET"])
@login_required
def get_dataAPI():
    devs = []
    for device in devices:
        data = {
            "name": device.name,
            "lastSignal": None if device.lastSignal == None else device.lastSignal.strftime("%Y-%m-%dT%H:%M:%S.0")
        }
        devs.append(json.dumps(data))

    openedList = []
    for opened in db.session.query(Opened).order_by(desc("time")).limit(5).all():
        data = {
            "time": opened.time.strftime("%d/%m/%Y %H:%M:%S"),
            "name": opened.device.name if opened.devicename == None else opened.devicename
        }
        openedList.append(json.dumps(data))

    return Response(
        json.dumps(
            {
                "devices": devs,
                "opened": openedList
            }
        ),
        content_type="application/json", status=200
    )
