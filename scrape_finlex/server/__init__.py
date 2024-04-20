from os import environ
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

from . import views
from .. import Config, do_scrape


def server_main():
    """Run the Flask app."""
    return app


def prod_main():
    """Run the Flask app in production."""
    port = environ["PORT"]
    if not port:
        port = 5000
    port = int(port)
    from waitress import serve

    serve(app, host="0.0.0.0", port=port)
