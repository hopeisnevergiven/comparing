"""
KoG Compare — Local Dev Server
Serves index.html AND handles /api/proxy — same path as Vercel.

Install:
    pip install flask requests

Run:
    python server.py

Then open:  http://localhost:5000
"""

from flask import Flask, request, Response, send_file
from urllib.parse import urlparse
import requests
import logging
import os

# ── Config ────────────────────────────────────────────────────────────────────
PORT         = 5000
ALLOWED_HOST = "www.ravenkog.com"
TIMEOUT      = 9

FORWARD_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer":         f"https://{ALLOWED_HOST}/",
}

# ── App ───────────────────────────────────────────────────────────────────────
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")


@app.after_request
def cors(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    return response


# ── Serve index.html at root ──────────────────────────────────────────────────
@app.route("/")
def index():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    return send_file(html_path)


# ── Proxy logic (shared) ──────────────────────────────────────────────────────
def _proxy():
    url = request.args.get("url", "").strip()

    if not url:
        return Response('{"error":"Missing ?url= parameter"}', 400, mimetype="application/json")

    if urlparse(url).netloc != ALLOWED_HOST:
        return Response('{"error":"URL not allowed"}', 403, mimetype="application/json")

    try:
        logging.info(f"→ {url}")
        resp  = requests.get(url, headers=FORWARD_HEADERS, timeout=TIMEOUT)
        ctype = resp.headers.get("Content-Type", "application/json")
        logging.info(f"← {resp.status_code}")
        return Response(resp.text, status=resp.status_code, mimetype=ctype)

    except requests.Timeout:
        return Response('{"error":"Upstream timed out"}', 504, mimetype="application/json")
    except requests.ConnectionError:
        return Response('{"error":"Could not reach ravenkog.com"}', 502, mimetype="application/json")
    except Exception as e:
        return Response(f'{{"error":"{e}"}}', 500, mimetype="application/json")


# ── /api/proxy  — matches Vercel path used in index.html ─────────────────────
@app.route("/api/proxy")
def proxy_vercel():
    return _proxy()


# ── /proxy  — kept for convenience ───────────────────────────────────────────
@app.route("/proxy")
def proxy_local():
    return _proxy()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 52)
    print("  KoG Compare — Local Dev Server")
    print(f"  ➜  http://localhost:{PORT}")
    print("  Press Ctrl-C to stop")
    print("=" * 52)
    app.run(host="0.0.0.0", port=PORT, debug=False)