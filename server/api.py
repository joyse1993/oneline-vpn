#!/usr/bin/env python3
"""Oneline VPN — Server REST API for web panel integration."""

import os
import sys
import json
import hashlib
import secrets
import subprocess
from functools import wraps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from wg_manager import (
    add_client, remove_client, list_clients,
    get_client_config, load_clients, WG_DIR
)

app = Flask(__name__)
app.secret_key = os.environ.get("API_SECRET", secrets.token_hex(32))

API_TOKENS_FILE = os.path.join(WG_DIR, "api_tokens.json")
API_PORT = int(os.environ.get("API_PORT", 8443))


def load_api_tokens() -> dict:
    if not os.path.exists(API_TOKENS_FILE):
        return {}
    with open(API_TOKENS_FILE) as f:
        return json.load(f)


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-API-Key", "")
        if not token:
            token = request.args.get("api_key", "")

        tokens = load_api_tokens()
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        if not token or token_hash not in tokens:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "Oneline VPN"})


@app.route("/api/server/status")
@require_auth
def server_status():
    try:
        wg_output = subprocess.check_output("wg show wg0", shell=True, text=True)
        active = True
    except Exception:
        wg_output = ""
        active = False

    clients = list_clients()
    return jsonify({
        "active": active,
        "total_clients": len(clients),
        "wg_status": wg_output,
    })


@app.route("/api/clients", methods=["GET"])
@require_auth
def api_list_clients():
    clients = list_clients()
    return jsonify({"clients": clients})


@app.route("/api/clients", methods=["POST"])
@require_auth
def api_add_client():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "name required"}), 400

    name = data["name"].strip().replace(" ", "_")
    if not name.isalnum() and "_" not in name:
        return jsonify({"error": "name must be alphanumeric"}), 400

    try:
        result = add_client(name)
        return jsonify({
            "success": True,
            "client": result,
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/clients/<name>", methods=["DELETE"])
@require_auth
def api_remove_client(name):
    if remove_client(name):
        return jsonify({"success": True})
    return jsonify({"error": "Client not found"}), 404


@app.route("/api/clients/<name>/config")
@require_auth
def api_get_config(name):
    config = get_client_config(name)
    if config:
        return jsonify({"name": name, "config": config})
    return jsonify({"error": "Client not found"}), 404


@app.route("/api/clients/<name>/qr")
@require_auth
def api_get_qr(name):
    """Return QR code as base64 PNG for embedding in web panel."""
    config = get_client_config(name)
    if not config:
        return jsonify({"error": "Client not found"}), 404

    try:
        import base64
        qr_png = subprocess.check_output(
            f"echo '{config}' | qrencode -t PNG -o -",
            shell=True,
        )
        b64 = base64.b64encode(qr_png).decode()
        return jsonify({
            "name": name,
            "qr_base64": b64,
            "qr_data_uri": f"data:image/png;base64,{b64}",
        })
    except Exception:
        return jsonify({"error": "qrencode not installed"}), 500


@app.route("/api/stats")
@require_auth
def api_stats():
    """WireGuard transfer stats per peer."""
    try:
        output = subprocess.check_output(
            "wg show wg0 transfer", shell=True, text=True
        )
    except Exception:
        return jsonify({"error": "WireGuard not running"}), 500

    clients = load_clients()
    pubkey_to_name = {c["public_key"]: n for n, c in clients.items()}

    stats = []
    for line in output.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) >= 3:
            pubkey, rx, tx = parts[0], int(parts[1]), int(parts[2])
            name = pubkey_to_name.get(pubkey, "unknown")
            stats.append({
                "name": name,
                "received_bytes": rx,
                "sent_bytes": tx,
                "received_mb": round(rx / 1048576, 2),
                "sent_mb": round(tx / 1048576, 2),
            })

    return jsonify({"stats": stats})


def generate_api_token():
    token = secrets.token_hex(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    tokens = load_api_tokens()
    tokens[token_hash] = {"created": subprocess.check_output("date -Iseconds", shell=True, text=True).strip()}
    with open(API_TOKENS_FILE, "w") as f:
        json.dump(tokens, f, indent=2)
    return token


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "gen-token":
        token = generate_api_token()
        print(f"\nAPI Token (save this, it won't be shown again):\n\n  {token}\n")
    else:
        print(f"Oneline VPN API starting on port {API_PORT}")
        app.run(host="0.0.0.0", port=API_PORT, ssl_context="adhoc" if os.path.exists("/etc/ssl") else None)
