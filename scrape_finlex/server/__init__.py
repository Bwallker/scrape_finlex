from os import environ
from flask import Flask

app = Flask(__name__)

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
