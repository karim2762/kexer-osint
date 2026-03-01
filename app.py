from flask import Flask, render_template, request, Response
import requests
import os
import json
import re
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from resources.site import sites

app = Flask(__name__)

OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# -------------------------------
# Advanced Username Intelligence
# -------------------------------
def analyze_username(username):
    has_numbers = any(c.isdigit() for c in username)
    has_special = any(not c.isalnum() for c in username)

    birth_year = "Unknown"
    year_match = re.search(r"(19\d{2}|20\d{2})", username)
    if year_match:
        birth_year = year_match.group()

    entropy = len(set(username)) / len(username)
    entropy_score = round(entropy, 2)

    bot_probability = round((1 - entropy) * 100)
    human_likelihood = 100 - bot_probability

    # Risk evaluation
    risk = "Low"
    if has_numbers:
        risk = "Medium"
    if has_special:
        risk = "High"

    # OSINT score
    score = 50
    if not has_numbers:
        score += 10
    if not has_special:
        score += 10
    if entropy > 0.6:
        score += 20
    if birth_year != "Unknown":
        score += 10

    score = min(score, 100)

    return {
        "length": len(username),
        "has_numbers": has_numbers,
        "has_special_chars": has_special,
        "possible_birth_year": birth_year,
        "risk_level": risk,
        "entropy_score": entropy_score,
        "bot_probability": bot_probability,
        "human_likelihood": human_likelihood,
        "osint_score": score
    }


# -------------------------------
# Check a single site
# -------------------------------
def check_site(site, url, username):
    target = url.format(username=username)

    try:
        r = requests.get(target, timeout=6)

        if r.status_code == 200 and username.lower() in r.text.lower():
            status = "FOUND"
        elif r.status_code == 200:
            status = "POSSIBLE"
        else:
            status = "NOT FOUND"

    except:
        status = "ERROR"

    return {
        "site": site,
        "url": target,
        "status": status
    }


# -------------------------------
# Live Scan Stream
# -------------------------------
def scan_stream(username):
    results = []
    total = len(sites)

    intelligence = analyze_username(username)

    yield f"data: {json.dumps({'type':'log','message':'Initializing KEXER OSINT Engine...'})}\n\n"
    yield f"data: {json.dumps({'type':'log','message':f'Target: {username}'})}\n\n"

    yield f"data: {json.dumps({'type':'log','message':'Running intelligence analysis...'})}\n\n"
    yield f"data: {json.dumps({'type':'log','message':f'Entropy Score: {intelligence['entropy_score']}'})}\n\n"
    yield f"data: {json.dumps({'type':'log','message':f'Bot Probability: {intelligence['bot_probability']}%'})}\n\n"
    yield f"data: {json.dumps({'type':'log','message':f'OSINT Score: {intelligence['osint_score']}/100'})}\n\n"

    yield f"data: {json.dumps({'type':'log','message':'Launching parallel scan...'})}\n\n"

    with ThreadPoolExecutor(max_workers=15) as executor:

        futures = [
            executor.submit(check_site, site, url, username)
            for site, url in sites.items()
        ]

        completed = 0

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1

            yield f"data: {json.dumps({
                'type':'result',
                'site': result['site'],
                'status': result['status'],
                'url': result['url'],
                'total': total
            })}\n\n"

    data = {
        "username": username,
        "intelligence": intelligence,
        "results": results
    }

    with open(f"{OUTPUT_FOLDER}/{username}.json", "w") as f:
        json.dump(data, f)

    yield f"data: {json.dumps({'type':'done'})}\n\n"


# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scan")
def scan():
    username = request.args.get("username")
    return render_template("scan.html", username=username)


@app.route("/scan_stream")
def scan_stream_route():
    username = request.args.get("username")
    return Response(scan_stream(username), mimetype="text/event-stream")


@app.route("/report/<username>")
def report(username):
    path = f"{OUTPUT_FOLDER}/{username}.json"

    if not os.path.exists(path):
        return "Report not found. Run scan first."

    with open(path) as f:
        data = json.load(f)

    return render_template("report.html", data=data)


# -------------------------------
# Start server
# -------------------------------
app.run(host="0.0.0.0", port=5000, debug=True)