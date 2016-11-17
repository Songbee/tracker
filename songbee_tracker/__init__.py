from flask import Flask
import click

from .models import db
from .api import bp as api_bp
from .admin import admin


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://postgres@db"
app.debug = True
app.secret_key = "FOOBAR"

db.init_app(app)
app.register_blueprint(api_bp, url_prefix="/api/v1")
admin.init_app(app)


@app.route("/")
def index():
    return """
    <form action="/api/v1/releases" method="POST" enctype="multipart/form-data">
        <input type="file" name="torrent"><br>
        <input type="submit">
    </form>
    """


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
