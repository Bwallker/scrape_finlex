from io import BytesIO
from typing import Any
from . import app
from ..cli import Config, do_scrape
from flask import render_template, request, send_file, Response


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/api/scrape", methods=["GET"])
def scrape() -> Response | tuple[str, int]:
    url = request.args.get("url")
    if url is None:
        return "No URL provided.", 400
    output_file_name = request.args.get("output-file-name")
    if output_file_name is None:
        output_file_name = "output.csv"
    output_file = BytesIO()
    config = Config(url, output_file, False)
    try:
        do_scrape(config)
        return send_file(
            output_file, as_attachment=True, download_name=output_file_name
        )
    finally:
        output_file.close()
