from flask_api import FlaskAPI
from flask_migrate import Migrate

from .models import db
from .api import bp as api_bp
from .admin import admin
from . import config

__version__ = "0.1.0"


app = FlaskAPI(__name__)
app.config.from_object(config)

db.init_app(app)
migrate = Migrate(app, db)
app.register_blueprint(api_bp, url_prefix="/api/v1")
admin.init_app(app)


@app.route("/")
def index():
    banner = app.config["BANNER"].format(version=__version__)
    return banner, 200, {"Content-Type": "text/plain"}
