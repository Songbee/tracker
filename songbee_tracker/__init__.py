from flask import Flask
import click

from .models import db
from .api import bp as api_bp
from .admin import admin
from . import config

__version__ = "0.1.0"


app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
app.register_blueprint(api_bp, url_prefix="/api/v1")
admin.init_app(app)


@app.route("/")
def index():
    banner = app.config["BANNER"].format(version=__version__)
    return banner, 200, {"Content-Type": "text/plain"}


@app.cli.command()
@click.option("--drop-all", is_flag=True)
@click.option("--fixtures", is_flag=True)
def initdb(drop_all, fixtures):
    """Initialize the database."""
    # from .models import Release

    if drop_all:
        click.echo("Dropping old tables...")
        db.drop_all()

    click.echo("Creating tables...")
    db.create_all()

    if fixtures:
        click.echo("No fixtures for now! Upload something by yourself.")

    click.echo("Done!")
