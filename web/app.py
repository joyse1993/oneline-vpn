#!/usr/bin/env python3
"""Oneline VPN — Web Panel (Landing + Dashboard + Admin)."""

import os
import sys
import json
import hashlib
import secrets
import time
import base64
import subprocess
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify, flash
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.json")
SERVERS_FILE = os.path.join(DATA_DIR, "servers.json")
KEYS_FILE = os.path.join(DATA_DIR, "keys.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "oneline2025")

API_URL = os.environ.get("VPN_API_URL", "http://localhost:8443")
API_KEY = os.environ.get("VPN_API_KEY", "")

PLANS = {
    "free": {"name": "Free", "devices": 1, "price": 0, "speed": "50 Mbps", "features": ["1 device", "50 Mbps", "Basic support"]},
    "pro": {"name": "Pro", "devices": 5, "price": 4.99, "speed": "Unlimited", "features": ["5 devices", "Unlimited speed", "No logs", "Priority support"]},
    "business": {"name": "Business", "devices": 20, "price": 14.99, "speed": "Unlimited", "features": ["20 devices", "Unlimited speed", "No logs", "Dedicated IP", "24/7 support", "Admin panel"]},
}


def _hash(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def load_json(path: str) -> dict | list:
    if not os.path.exists(path):
        return {} if path != KEYS_FILE else []
    with open(path) as f:
        return json.load(f)


def save_json(path: str, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_users() -> dict:
    return load_json(USERS_FILE)


def save_users(users: dict):
    save_json(USERS_FILE, users)


def get_keys() -> list:
    data = load_json(KEYS_FILE)
    return data if isinstance(data, list) else []


def save_keys(keys: list):
    save_json(KEYS_FILE, keys)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


def api_request(method: str, endpoint: str, data=None):
    """Call the VPN server API."""
    import requests
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    url = f"{API_URL}{endpoint}"
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=10, verify=False)
        elif method == "POST":
            r = requests.post(url, headers=headers, json=data, timeout=10, verify=False)
        elif method == "DELETE":
            r = requests.delete(url, headers=headers, timeout=10, verify=False)
        else:
            return None
        return r.json()
    except Exception:
        return None


# ─── Public Routes ─────────────────────────────────────────

@app.route("/")
def index():
    return render_template("landing.html", plans=PLANS)


@app.route("/download")
def download():
    return render_template("download.html")


# ─── Auth Routes ───────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        username = request.form.get("username", "").strip()

        if not email or not password or not username:
            flash("All fields required", "error")
            return redirect(url_for("register"))

        users = get_users()
        if email in users:
            flash("Email already registered", "error")
            return redirect(url_for("register"))

        users[email] = {
            "username": username,
            "password": _hash(password),
            "plan": "free",
            "devices": [],
            "created": datetime.utcnow().isoformat(),
        }
        save_users(users)

        session["user"] = email
        session["username"] = username
        return redirect(url_for("dashboard"))

    return render_template("landing.html", plans=PLANS, show_register=True)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        users = get_users()
        user = users.get(email)

        if user and user["password"] == _hash(password):
            session["user"] = email
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))

        flash("Invalid email or password", "error")
        return redirect(url_for("login"))

    return render_template("landing.html", plans=PLANS, show_login=True)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ─── Dashboard Routes ─────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    users = get_users()
    user = users.get(session["user"], {})
    keys = [k for k in get_keys() if k.get("user") == session["user"]]
    plan = PLANS.get(user.get("plan", "free"), PLANS["free"])
    return render_template(
        "dashboard.html",
        user=user,
        email=session["user"],
        keys=keys,
        plan=plan,
        plans=PLANS,
    )


@app.route("/dashboard/generate-key", methods=["POST"])
@login_required
def generate_key():
    device_name = request.form.get("device_name", "device").strip().replace(" ", "_")
    platform = request.form.get("platform", "macos")
    email = session["user"]

    users = get_users()
    user = users.get(email, {})
    user_keys = [k for k in get_keys() if k.get("user") == email]
    plan = PLANS.get(user.get("plan", "free"), PLANS["free"])

    if len(user_keys) >= plan["devices"]:
        flash(f"Device limit reached ({plan['devices']}). Upgrade your plan.", "error")
        return redirect(url_for("dashboard"))

    unique_name = f"{email.split('@')[0]}_{device_name}_{int(time.time())}"

    result = api_request("POST", "/api/clients", {"name": unique_name})

    keys = get_keys()
    key_entry = {
        "id": secrets.token_hex(8),
        "user": email,
        "device_name": device_name,
        "platform": platform,
        "internal_name": unique_name,
        "created": datetime.utcnow().isoformat(),
    }

    if result and result.get("success"):
        key_entry["config"] = result["client"]["config"]
        key_entry["ip"] = result["client"]["ip"]
        key_entry["status"] = "active"
    else:
        key_entry["config"] = _generate_demo_config(unique_name)
        key_entry["ip"] = "10.66.66.x"
        key_entry["status"] = "pending_server"

    keys.append(key_entry)
    save_keys(keys)

    flash(f"Key generated for {device_name}!", "success")
    return redirect(url_for("dashboard"))


@app.route("/dashboard/key/<key_id>")
@login_required
def get_key_details(key_id):
    keys = get_keys()
    key = next((k for k in keys if k["id"] == key_id and k["user"] == session["user"]), None)
    if not key:
        return jsonify({"error": "Key not found"}), 404

    qr_b64 = ""
    config = key.get("config", "")
    if config:
        try:
            qr_png = subprocess.check_output(
                f"echo '{config}' | qrencode -t PNG -o -",
                shell=True, stderr=subprocess.DEVNULL,
            )
            qr_b64 = base64.b64encode(qr_png).decode()
        except Exception:
            qr_b64 = ""

    return jsonify({
        "id": key["id"],
        "device_name": key["device_name"],
        "platform": key["platform"],
        "ip": key.get("ip", ""),
        "config": config,
        "qr_base64": qr_b64,
        "status": key.get("status", "active"),
        "created": key.get("created", ""),
    })


@app.route("/dashboard/key/<key_id>/delete", methods=["POST"])
@login_required
def delete_key(key_id):
    keys = get_keys()
    key = next((k for k in keys if k["id"] == key_id and k["user"] == session["user"]), None)
    if not key:
        flash("Key not found", "error")
        return redirect(url_for("dashboard"))

    if key.get("status") == "active":
        api_request("DELETE", f"/api/clients/{key['internal_name']}")

    keys = [k for k in keys if k["id"] != key_id]
    save_keys(keys)

    flash("Device removed", "success")
    return redirect(url_for("dashboard"))


# ─── Admin Routes ──────────────────────────────────────────

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == ADMIN_USER and password == ADMIN_PASS:
            session["is_admin"] = True
            return redirect(url_for("admin_panel"))
        flash("Invalid credentials", "error")
    return render_template("admin_login.html")


@app.route("/admin")
@admin_required
def admin_panel():
    users = get_users()
    keys = get_keys()
    server_status = api_request("GET", "/api/server/status")

    total_users = len(users)
    total_keys = len(keys)
    active_keys = len([k for k in keys if k.get("status") == "active"])

    plan_counts = {}
    for u in users.values():
        p = u.get("plan", "free")
        plan_counts[p] = plan_counts.get(p, 0) + 1

    monthly_revenue = sum(
        PLANS.get(u.get("plan", "free"), {}).get("price", 0)
        for u in users.values()
    )

    return render_template(
        "admin.html",
        users=users,
        keys=keys,
        total_users=total_users,
        total_keys=total_keys,
        active_keys=active_keys,
        plan_counts=plan_counts,
        monthly_revenue=monthly_revenue,
        server_status=server_status,
    )


@app.route("/admin/users/<email>/delete", methods=["POST"])
@admin_required
def admin_delete_user(email):
    users = get_users()
    if email in users:
        del users[email]
        save_users(users)
        keys = [k for k in get_keys() if k.get("user") != email]
        save_keys(keys)
    return redirect(url_for("admin_panel"))


@app.route("/admin/users/<email>/plan", methods=["POST"])
@admin_required
def admin_change_plan(email):
    new_plan = request.form.get("plan", "free")
    users = get_users()
    if email in users:
        users[email]["plan"] = new_plan
        save_users(users)
    return redirect(url_for("admin_panel"))


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))


def _generate_demo_config(name: str) -> str:
    return f"""[Interface]
PrivateKey = <will be generated when server connects>
Address = 10.66.66.x/32
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = <server public key>
Endpoint = YOUR_SERVER_IP:51820
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25

# Device: {name}
# Status: Pending server connection
# Connect your VPS and re-generate this key
"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
