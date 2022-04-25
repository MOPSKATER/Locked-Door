import os
from pywebpush import webpush
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length
from wtforms import StringField, PasswordField, SubmitField


DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH = os.path.join(
    os.getcwd(), "private_key.txt")
DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH = os.path.join(
    os.getcwd(), "public_key.txt")

VAPID_PRIVATE_KEY = open(
    DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH, "r+").readline().strip("\n")
VAPID_PUBLIC_KEY = open(
    DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH, "r+").read().strip("\n")

VAPID_CLAIMS = {
    "sub": "mail@localhost"
}


class LoginForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Benutzername"}
    )

    password = PasswordField(
        validators=[InputRequired(), Length(min=8, max=20)],
        render_kw={"placeholder": "Passwort"}
    )

    submit = SubmitField("Login")


def send_web_push(subscription_information, message_body):
    return webpush(
        subscription_info=subscription_information,
        data=message_body,
        vapid_private_key=VAPID_PRIVATE_KEY,
        vapid_claims=VAPID_CLAIMS
    )
