from flask import Flask, render_template, request, Response
import json
import os
from engine import scan_sites
from intelligence import analyze_username
from database import load_sites

app = Flask(__name__)

SITES = load_sites()

os.makedirs("reports", exist_ok=True)
os.makedirs("history", exist_ok=True)


def stream_scan(username):

    results = []

    for result in scan_sites(username, SITES):
        results.append(result)
        yield f"data: {json.dumps(result)}\n\n"

    intel = analyze_username(username)

    report = {
        "username": username,
        "intelligence": intel,
        "results": results
    }

    with open(f"reports/{username}.json", "w") as f:
        json.dump(report, f, indent=4)

    with open(f"history/{username}.json", "w") as f:
        json.dump(report, f)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scan")
def scan():
    username = request.args.get("username")
    return render_template("scan.html", username=username)


@app.route("/stream")
def stream():
    username = request.args.get("username")
    return Response(stream_scan(username), mimetype="text/event-stream")


@app.route("/report/<username>")
def report(username):
    path = f"reports/{username}.json"

    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        return render_template("report.html", data=data)

    return "Report not found"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
