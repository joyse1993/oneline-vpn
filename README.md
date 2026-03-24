# ◆ Oneline VPN — Self-Hosted VPN Service

<div align="center">

### Your Internet. Your Rules.

A complete, self-hosted VPN solution built on WireGuard.
Web panel + Admin dashboard + macOS client + all platforms.

**Zero logs · ISP invisible · Open source**

[Features](#features) · [Quick Start](#quick-start) · [Architecture](#architecture) · [Pricing](#selling)

---

</div>

## Features

| Feature | Description |
|---------|-------------|
| **WireGuard Protocol** | Fastest VPN protocol — built into Linux kernel, 4x faster than OpenVPN |
| **Traffic Obfuscation** | wstunnel wraps VPN in WebSocket — ISPs see HTTPS, not VPN |
| **DNS over TLS** | Unbound resolver forwards to Cloudflare DoT + Google DoT |
| **Zero Logs** | No traffic logs, no DNS logs, no timestamps, no IP logs |
| **Web Dashboard** | Users register, generate keys, scan QR codes |
| **Admin Panel** | Manage users, plans (Free/Pro/Business), view revenue + stats |
| **macOS Client** | Native menu bar app — connect, disconnect, kill switch, auto-connect |
| **All Platforms** | macOS, Windows, Android, iOS via WireGuard configs + QR |
| **Kill Switch** | Blocks all traffic if VPN drops (macOS client) |
| **Commercial Ready** | 3-tier pricing, user management, MIT license — run as SaaS |

## Tech Stack

| Component | Technology |
|-----------|-----------|
| VPN Server | WireGuard + wstunnel + Unbound DNS |
| Web Panel | Python Flask, Jinja2, HTML5/CSS3/JS |
| macOS Client | Python + rumps (menu bar framework) |
| Database | JSON files (no external DB needed) |
| Setup | Single `setup.sh` — one command |

## Quick Start

### 1. Deploy VPN Server

Buy a VPS ($3-5/month) — Hetzner, DigitalOcean, or Vultr. Then:

```bash
cd server
sudo bash setup.sh
```

**What this does:**
- Installs WireGuard
- Configures DNS over TLS (Unbound → Cloudflare + Google)
- Installs wstunnel for traffic obfuscation
- Sets up firewall (ufw)
- Generates first client config + QR code

### 2. Run Web Panel

```bash
cd web
pip install flask requests
python app.py
```

Open `http://localhost:5000`

**Environment variables:**
```
VPN_API_URL=https://YOUR_VPS_IP:8443
VPN_API_KEY=your-api-token
ADMIN_USER=admin
ADMIN_PASS=your-password
SECRET_KEY=random-secret
```

### 3. macOS Client

```bash
cd client
pip install rumps
python nexusvpn.py
```

### 4. Other Platforms

| Platform | How to connect |
|----------|---------------|
| **Android** | Dashboard → Add Device → Scan QR with WireGuard app |
| **iOS** | Dashboard → Add Device → Scan QR with WireGuard app |
| **Windows** | Dashboard → Download .conf → Import into WireGuard |
| **macOS** | Use Oneline client or import .conf into WireGuard |

## Architecture

```
nexus_vpn/
├── server/                 # VPS deployment
│   ├── setup.sh            # One-command installer (WG + wstunnel + Unbound)
│   ├── manage.py           # CLI: add/remove/list clients
│   ├── wg_manager.py       # WireGuard key/config management
│   └── api.py              # REST API for web panel
│
├── web/                    # Web panel (Flask)
│   ├── app.py              # Auth, dashboard, admin, API integration
│   ├── templates/          # Landing, Dashboard, Admin, Download
│   └── static/             # Premium CSS + JS
│
├── client/                 # macOS desktop client
│   ├── nexusvpn.py         # Entry point
│   ├── vpn_engine.py       # WireGuard connection engine
│   ├── tray.py             # Menu bar app (rumps)
│   └── config.py           # Config storage
│
└── configs/                # Example configs + setup guide
    ├── SETUP_GUIDE.md
    └── *.conf              # Per-platform examples
```

## Web Panel

### Landing Page
- Animated hero with gradient text
- 6 feature cards with hover effects
- Comparison table vs NordVPN/ProtonVPN/Cloudflare
- 3-tier pricing (Free / $4.99 Pro / $14.99 Business)
- Testimonials from users
- FAQ accordion
- CTA banner
- Full footer with links

### User Dashboard
- Device management — add/remove
- Config viewer with copy + download
- QR code generation for mobile
- Plan status + upgrade prompts
- Quick setup instructions

### Admin Panel
- Revenue tracking
- User management (change plan, delete)
- Plan distribution overview
- Server status (WireGuard active/offline)
- All keys listing

## Selling

**Recommended price: $99 — $199**

Target buyers:
- Privacy-conscious individuals
- Small businesses needing corporate VPN
- Developers wanting self-hosted VPN
- Resellers who want to launch a VPN service

## Server Requirements

- Ubuntu 20.04+ or Debian 11+
- 512 MB RAM minimum
- Root access
- VPS: $3-5/month

## License

MIT License — commercial use, modification, and resale allowed.
