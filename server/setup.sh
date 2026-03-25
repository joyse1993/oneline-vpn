#!/bin/bash
# ═══════════════════════════════════════════════════════════
# 19 VPN — Server Auto-Setup Script v2.0
# Supports: Ubuntu 20.04/22.04/24.04, Debian 11/12
# Usage: sudo bash setup.sh
# ═══════════════════════════════════════════════════════════

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

WG_INTERFACE="wg0"
WG_PORT=51820
OBFS_PORT=443
WG_SUBNET="10.66.66.0/24"
WG_SERVER_IP="10.66.66.1"
WG_DIR="/etc/wireguard"
WSTUNNEL_VERSION="10.1.0"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║                                                  ║"
echo "║     🛡  19 VPN  — Server Setup v2.0                ║"
echo "║     WireGuard + WebSocket Obfuscation            ║"
echo "║                                                  ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# ─── Check root ────────────────────────────────────────

if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}[!] Run as root: sudo bash setup.sh${NC}"
    exit 1
fi

# ─── Detect system ─────────────────────────────────────

if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS=$ID
else
    echo -e "${RED}[!] Unsupported OS${NC}"
    exit 1
fi

SERVER_NIC=$(ip -4 route ls | grep default | awk '{print $5}' | head -1)
SERVER_PUB_IP=$(curl -s4 ifconfig.me || curl -s4 icanhazip.com || echo "UNKNOWN")

echo -e "${GREEN}[+] OS:        ${BOLD}$OS $VERSION_ID${NC}"
echo -e "${GREEN}[+] Public IP: ${BOLD}$SERVER_PUB_IP${NC}"
echo -e "${GREEN}[+] NIC:       ${BOLD}$SERVER_NIC${NC}"
echo ""

# ─── Install Dependencies ──────────────────────────────

echo -e "${CYAN}[1/8] Installing packages...${NC}"
apt-get update -qq
apt-get install -y -qq \
    wireguard wireguard-tools qrencode \
    iptables python3 python3-pip \
    curl wget ufw unbound \
    > /dev/null 2>&1
echo -e "${GREEN}  ✓ Packages installed${NC}"

# ─── DNS over HTTPS (Unbound) ──────────────────────────

echo -e "${CYAN}[2/8] Configuring secure DNS (Unbound)...${NC}"

cat > /etc/unbound/unbound.conf.d/19vpn.conf << 'DNSEOF'
server:
    num-threads: 2
    interface: 10.66.66.1
    access-control: 10.66.66.0/24 allow
    access-control: 127.0.0.0/8 allow
    hide-identity: yes
    hide-version: yes
    harden-glue: yes
    harden-dnssec-stripped: yes
    use-caps-for-id: yes
    prefetch: yes
    cache-min-ttl: 3600
    cache-max-ttl: 86400
    private-address: 10.0.0.0/8
    private-address: 172.16.0.0/12
    private-address: 192.168.0.0/16

    # Forward to Cloudflare DoT
    forward-zone:
        name: "."
        forward-tls-upstream: yes
        forward-addr: 1.1.1.1@853#cloudflare-dns.com
        forward-addr: 1.0.0.1@853#cloudflare-dns.com
        forward-addr: 8.8.8.8@853#dns.google
        forward-addr: 8.8.4.4@853#dns.google
DNSEOF

systemctl enable unbound > /dev/null 2>&1
systemctl restart unbound > /dev/null 2>&1
echo -e "${GREEN}  ✓ DNS over TLS (Unbound → Cloudflare + Google)${NC}"

# ─── Enable IP Forwarding ──────────────────────────────

echo -e "${CYAN}[3/8] Enabling IP forwarding...${NC}"
sysctl -w net.ipv4.ip_forward=1 > /dev/null
sysctl -w net.ipv6.conf.all.forwarding=1 > /dev/null
sed -i '/net.ipv4.ip_forward/d' /etc/sysctl.conf
sed -i '/net.ipv6.conf.all.forwarding/d' /etc/sysctl.conf
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
echo "net.ipv6.conf.all.forwarding=1" >> /etc/sysctl.conf
echo -e "${GREEN}  ✓ IP forwarding enabled${NC}"

# ─── Generate Server Keys ──────────────────────────────

echo -e "${CYAN}[4/8] Generating WireGuard keys...${NC}"
mkdir -p $WG_DIR
chmod 700 $WG_DIR

SERVER_PRIVKEY=$(wg genkey)
SERVER_PUBKEY=$(echo "$SERVER_PRIVKEY" | wg pubkey)

echo "$SERVER_PRIVKEY" > $WG_DIR/server_private.key
echo "$SERVER_PUBKEY" > $WG_DIR/server_public.key
chmod 600 $WG_DIR/server_private.key

echo '{}' > $WG_DIR/clients.json
echo -e "${GREEN}  ✓ Server keys generated${NC}"

# ─── Create WireGuard Config ───────────────────────────

echo -e "${CYAN}[5/8] Creating WireGuard config...${NC}"

cat > $WG_DIR/$WG_INTERFACE.conf << EOF
[Interface]
PrivateKey = $SERVER_PRIVKEY
Address = $WG_SERVER_IP/24
ListenPort = $WG_PORT
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o $SERVER_NIC -j MASQUERADE; ip6tables -A FORWARD -i %i -j ACCEPT; ip6tables -t nat -A POSTROUTING -o $SERVER_NIC -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o $SERVER_NIC -j MASQUERADE; ip6tables -D FORWARD -i %i -j ACCEPT; ip6tables -t nat -D POSTROUTING -o $SERVER_NIC -j MASQUERADE
EOF

chmod 600 $WG_DIR/$WG_INTERFACE.conf
echo -e "${GREEN}  ✓ WireGuard config created${NC}"

# ─── Start WireGuard ───────────────────────────────────

echo -e "${CYAN}[6/8] Starting WireGuard...${NC}"
systemctl enable wg-quick@$WG_INTERFACE > /dev/null 2>&1
systemctl start wg-quick@$WG_INTERFACE > /dev/null 2>&1
echo -e "${GREEN}  ✓ WireGuard started${NC}"

# ─── Install wstunnel (Obfuscation) ────────────────────

echo -e "${CYAN}[7/8] Installing traffic obfuscation (wstunnel)...${NC}"

ARCH=$(dpkg --print-architecture)
if [[ "$ARCH" == "amd64" ]]; then
    WSTUNNEL_ARCH="x86_64-unknown-linux-gnu"
elif [[ "$ARCH" == "arm64" ]]; then
    WSTUNNEL_ARCH="aarch64-unknown-linux-gnu"
else
    WSTUNNEL_ARCH="x86_64-unknown-linux-gnu"
fi

WSTUNNEL_URL="https://github.com/erebe/wstunnel/releases/download/v${WSTUNNEL_VERSION}/wstunnel_${WSTUNNEL_VERSION}_linux_${WSTUNNEL_ARCH}.tar.gz"

if wget -qO /tmp/wstunnel.tar.gz "$WSTUNNEL_URL" 2>/dev/null; then
    tar -xzf /tmp/wstunnel.tar.gz -C /usr/local/bin/ wstunnel 2>/dev/null || true
    chmod +x /usr/local/bin/wstunnel 2>/dev/null || true
    rm -f /tmp/wstunnel.tar.gz

    cat > /etc/systemd/system/wstunnel.service << EOF
[Unit]
Description=19 VPN Obfuscation (wstunnel)
After=network.target wg-quick@wg0.service

[Service]
Type=simple
ExecStart=/usr/local/bin/wstunnel server --restrict-to 127.0.0.1:$WG_PORT wss://0.0.0.0:$OBFS_PORT
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable wstunnel > /dev/null 2>&1
    systemctl start wstunnel > /dev/null 2>&1
    echo -e "${GREEN}  ✓ wstunnel obfuscation active (port $OBFS_PORT)${NC}"
    echo -e "${GREEN}    ISP sees: regular HTTPS traffic${NC}"
    echo -e "${GREEN}    Reality: encrypted WireGuard VPN${NC}"
else
    echo -e "${YELLOW}  ⚠ wstunnel download failed — VPN works without it${NC}"
    echo -e "${YELLOW}    Obfuscation can be installed later${NC}"
fi

# ─── Firewall ──────────────────────────────────────────

echo -e "${CYAN}[8/8] Configuring firewall...${NC}"
ufw allow 22/tcp > /dev/null 2>&1
ufw allow $WG_PORT/udp > /dev/null 2>&1
ufw allow $OBFS_PORT/tcp > /dev/null 2>&1
ufw allow 8443/tcp > /dev/null 2>&1
ufw --force enable > /dev/null 2>&1
echo -e "${GREEN}  ✓ Firewall configured${NC}"

# ─── Copy Management Scripts ──────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/manage.py" ]]; then
    cp "$SCRIPT_DIR/manage.py" /usr/local/bin/19vpn-manage
    cp "$SCRIPT_DIR/wg_manager.py" /usr/local/bin/wg_manager.py
    chmod +x /usr/local/bin/19vpn-manage
fi

# ─── Create First Client ──────────────────────────────

CLIENT_PRIVKEY=$(wg genkey)
CLIENT_PUBKEY=$(echo "$CLIENT_PRIVKEY" | wg pubkey)
CLIENT_PSK=$(wg genpsk)
CLIENT_IP="10.66.66.2"

cat > $WG_DIR/client_default.conf << EOF
[Interface]
PrivateKey = $CLIENT_PRIVKEY
Address = $CLIENT_IP/32
DNS = $WG_SERVER_IP
MTU = 1280

[Peer]
PublicKey = $SERVER_PUBKEY
PresharedKey = $CLIENT_PSK
Endpoint = $SERVER_PUB_IP:$WG_PORT
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
EOF

chmod 600 $WG_DIR/client_default.conf

wg set $WG_INTERFACE peer $CLIENT_PUBKEY preshared-key <(echo "$CLIENT_PSK") allowed-ips $CLIENT_IP/32

cat >> $WG_DIR/$WG_INTERFACE.conf << EOF

# default
[Peer]
PublicKey = $CLIENT_PUBKEY
PresharedKey = $CLIENT_PSK
AllowedIPs = $CLIENT_IP/32
EOF

python3 -c "
import json
from datetime import datetime
clients = {'default': {
    'ip': '$CLIENT_IP',
    'public_key': '$CLIENT_PUBKEY',
    'psk': '$CLIENT_PSK',
    'created': datetime.utcnow().isoformat(),
}}
with open('$WG_DIR/clients.json', 'w') as f:
    json.dump(clients, f, indent=2)
"

# ─── Summary ──────────────────────────────────────────

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${GREEN}     🛡  19 VPN Server is READY!                   ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Server IP:       ${BOLD}$SERVER_PUB_IP${NC}"
echo -e "  WireGuard:       ${BOLD}Port $WG_PORT/UDP${NC}"
echo -e "  Obfuscation:     ${BOLD}Port $OBFS_PORT/TCP (WebSocket)${NC}"
echo -e "  DNS:             ${BOLD}Unbound → DoT (Cloudflare + Google)${NC}"
echo -e "  Subnet:          ${BOLD}$WG_SUBNET${NC}"
echo ""
echo -e "  Client config:   ${GREEN}$WG_DIR/client_default.conf${NC}"
echo ""
echo -e "  ${CYAN}QR code for mobile:${NC}"
echo ""
qrencode -t ansiutf8 < $WG_DIR/client_default.conf 2>/dev/null || echo "  (qrencode not available)"
echo ""
echo -e "${CYAN}──────────────────────────────────────────────────${NC}"
echo -e "  ${BOLD}Management commands:${NC}"
echo -e "  19vpn-manage add <name>     Add new client"
echo -e "  19vpn-manage remove <name>  Remove client"
echo -e "  19vpn-manage list           List all clients"
echo -e "  19vpn-manage qr <name>      Show QR code"
echo -e "${CYAN}──────────────────────────────────────────────────${NC}"
