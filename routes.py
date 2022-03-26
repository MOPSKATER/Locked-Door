import json
import flask
import flask_bcrypt as bcrypt
from __main__ import app, login_manager, db
from flask_login import current_user, login_required, login_user
from flask import Response, jsonify, render_template, request
from utility import LoginForm, Users, VAPID_PUBLIC_KEY, send_web_push

api_keys = open("apikeys.txt", "r").read().split("\n")


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, user.salt + form.password.data):
                login_user(user)
            return flask.redirect(flask.url_for('index'))
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
    api_key = request.args.get('api_key')
    if api_key and api_key in api_keys:
        command = request.args.get('command')
        if command == "alive":
            pass
        elif command == "alert":
            for user in Users.query.all():
                send_web_push(json.loads(user.token), user.username)
        return Response(status=200)
    return Response(status=403)


@app.route("/api/data", methods=["GET"])
def dataAPI():
    pass
