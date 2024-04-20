from io import BytesIO
from sys import stderr
from . import app
from ..cli import Config, do_scrape
from flask import render_template, request, send_file, Response


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/api/scrape", methods=["POST"])
def scrape() -> Response | tuple[str, int]:
    url = request.form.get("url")
    if url is None:
        return "No URL provided.", 400
    print("URL:", url, file=stderr)
    output_file_name = request.form.get("output-file-name")
    if output_file_name is None or output_file_name == "":
        output_file_name = "output.csv"
    if not output_file_name.endswith(".csv"):
        output_file_name += ".csv"
    output_file = BytesIO()
    config = Config(url, output_file, False)
    do_scrape(config)
    return send_file(output_file, as_attachment=True, download_name=output_file_name)
