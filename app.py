import os, re
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Replace with the exact GitHub Pages origin after publishing, e.g. https://username.github.io
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "").rstrip("/")
CORS(app, resources={r"/api/*": {"origins": [ALLOWED_ORIGIN] if ALLOWED_ORIGIN else []}},
     allow_headers=["Content-Type"], methods=["POST", "OPTIONS"])

# PRIVATE ANSWER KEY. Keep this backend repository private.
ANSWER_KEY = {
  1: "contractor01", 2: r".\PsExec64.exe -s -i cmd.exe", 3: "33",
  4: "PROGRAM", 5: "daV324982S3bh2", 6: "AES-256-CBC",
  7: "a5f41376d435dc6c61ef9ddf2c4a9543c7d68ec746e690fe391bf1604362742f95e61ead02c32dab646478048203fd0",
  8: "test", 9: "/mnt/c/Users", 10: "zlib", 11: "/proc/self/status",
  12: "SIGSEGV", 13: ".exe", 14: "gcc", 15: "*********DEBUGGED*********",
  16: "GCC: (Debian 10.2.1-6) 10.2.1 20210110", 17: ".31337",
  18: "16ftSEQ4ctQFDtVZiUBusQUjRrGhM3JYwe", 19: "TracerPid",
  20: "blitztide", 21: "getdents64", 22: "unlink"
}
def norm(v):
    return re.sub(r"\s+", " ", str(v or "").strip()).casefold()

@app.get("/health")
def health():
    return jsonify({"status":"ok"})

@app.post("/api/submit")
def submit():
    # Do not log request bodies; do not persist individual responses.
    data = request.get_json(silent=True) or {}
    name = re.sub(r"\s+", " ", str(data.get("name", "")).strip())[:100]
    answers = data.get("answers", {})
    if not name:
        return jsonify({"error":"Please enter your name."}), 400
    if not isinstance(answers, dict):
        return jsonify({"error":"Invalid submission."}), 400
    score = sum(1 for i, expected in ANSWER_KEY.items()
                if norm(answers.get(str(i), answers.get(i, ""))) == norm(expected))
    sheet_url = os.environ.get("GOOGLE_APPS_SCRIPT_URL", "").strip()
    secret = os.environ.get("GOOGLE_SHEETS_SHARED_SECRET", "").strip()
    if not sheet_url or not secret:
        return jsonify({"score":score,"total":22,"recorded":False,
                        "message":f"Score calculated: {score} / 22. Score-sheet recording is not configured."})
    try:
        r = requests.post(sheet_url, json={"name":name,"score":score,"secret":secret}, timeout=10)
        r.raise_for_status()
        if not r.json().get("ok"):
            raise RuntimeError("sheet bridge rejected submission")
    except Exception:
        app.logger.error("Google Sheets recording failed; request body intentionally omitted.")
        return jsonify({"error":"Your score was calculated, but the organizer could not save it. Please contact the organizer."}), 502
    return jsonify({"score":score,"total":22,"recorded":True,
                    "message":f"Submission complete — {score} / 22 correct. Your name and score were recorded. Individual answers were not saved."})
