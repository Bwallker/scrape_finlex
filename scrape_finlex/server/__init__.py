from os import environ
from flask import Flask

app = Flask(__name__)

from . import views
from .. import Config, do_scrape


def server_main():
    """Run the Flask app."""
    if __name__ == "__main__":
        port = environ["PORT"]
        if not port:
            port = 5000
        port = int(port)
        app.run(port=port)
    return app
