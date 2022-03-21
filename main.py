from flask import Flask
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = '6t76/&R6fnz7n)xqjK8(sa'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///access.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

import utility
import routes


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
