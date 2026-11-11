from flask import Flask
from config import config_by_name
from mission_control.extensions import db, migrate
from mission_control.routes import main_bp

def create_app(config_name="development"):
    app = Flask(__name__)

    config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main_bp)

    return app

