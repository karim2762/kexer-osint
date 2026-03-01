import os
import re
import json
from flask import Flask, request, Response
import httpx
import asyncio

from resources.site import sites  # your site dictionary

app = Flask(__name__)

MAX_WORKERS = int(os.environ.get("MAX_WORKERS", 5))
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", 6))


# -------------------------------
# Username intelligence
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

    risk = "Low"
    if has_numbers:
        risk = "Medium"
    if has_special:
        risk = "High"

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
# Async check site
# -------------------------------
async def check_site(client, site, url, username):
    target = url.format(username=username)
    try:
        r = await client.get(target, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200 and username.lower() in r.text.lower():
            status = "FOUND"
        elif r.status_code == 200:
            status = "POSSIBLE"
        else:
            status = "NOT FOUND"
    except httpx.RequestError:
        status = "ERROR"

    return {"site": site, "url": target, "status": status}


# -------------------------------
# Stream scan results
# -------------------------------
async def scan_stream_async(username):
    results = []
    total = len(sites)
    intelligence = analyze_username(username)

    yield f"data: {json.dumps({'type': 'log', 'message': 'Initializing KEXER OSINT Engine...'})}\n\n"
    yield f"data: {json.dumps({'type': 'log', 'message': f'Target: {username}'})}\n\n"
    yield f"data: {json.dumps({'type': 'log', 'message': f'Entropy Score: {intelligence['entropy_score']}'})}\n\n"
    yield f"data: {json.dumps({'type': 'log', 'message': f'Bot Probability: {intelligence['bot_probability']}%'})}\n\n"
    yield f"data: {json.dumps({'type': 'log', 'message': f'OSINT Score: {intelligence['osint_score']}/100'})}\n\n"
    yield f"data: {json.dumps({'type': 'log', 'message': 'Launching async scan...'})}\n\n"

    async with httpx.AsyncClient() as client:
        tasks = [check_site(client, site, url, username) for site, url in sites.items()]
        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
            yield f"data: {json.dumps({'type': 'result', 'site': result['site'], 'status': result['status'], 'url': result['url'], 'total': total})}\n\n"

    # send intelligence + results at the end
    yield f"data: {json.dumps({'type': 'done', 'username': username, 'intelligence': intelligence, 'results': results})}\n\n"


# -------------------------------
# Flask routes
# -------------------------------
@app.route("/")
def home():
    return {"message": "KEXER OSINT Serverless API"}


@app.route("/scan_stream")
def scan_stream_route():
    username = request.args.get("username")
    return Response(scan_stream_async(username), mimetype="text/event-stream")


# -------------------------------
# Export for Vercel
# -------------------------------
handler = app
