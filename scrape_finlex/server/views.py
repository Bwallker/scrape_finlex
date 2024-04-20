from io import BytesIO
from typing import Any
from . import app
from ..cli import Config, do_scrape
from flask import render_template, request, send_file, Response
from flask_cors import cross_origin


@app.route("/", methods=["GET"])
@cross_origin()
def index():
    return render_template("index.html")


@app.route("/api/scrape", methods=["POST"])
@cross_origin()
def scrape() -> Response | tuple[str, int]:
    url = request.form.get("url")
    if url is None:
        return "No URL provided.", 400
    output_file_name = request.form.get("output-file-name")
    if output_file_name is None or output_file_name == "":
        output_file_name = "output.csv"
    if not output_file_name.endswith(".csv"):
        output_file_name += ".csv"
    output_file = BytesIO()
    config = Config(url, output_file, False)
    do_scrape(config)
    response = send_file(
        output_file, as_attachment=True, download_name=output_file_name
    )
    response.headers.set("Content-Type", "text/csv")
    print("Returning response:", response)
    return response
