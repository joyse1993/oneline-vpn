#!/usr/bin/env python3
"""WireGuard key and config management for Oneline VPN."""

import subprocess
import ipaddress
import os
import json

WG_DIR = "/etc/wireguard"
WG_INTERFACE = "wg0"
CLIENTS_FILE = os.path.join(WG_DIR, "clients.json")
SERVER_PORT = 51820
DNS = "1.1.1.1, 8.8.8.8"
SUBNET = "10.66.66.0/24"


def _run(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True, text=True).strip()


def generate_keypair() -> tuple[str, str]:
    private = _run("wg genkey")
    public = _run(f"echo '{private}' | wg pubkey")
    return private, public


def generate_psk() -> str:
    return _run("wg genpsk")


def load_clients() -> dict:
    if not os.path.exists(CLIENTS_FILE):
        return {}
    with open(CLIENTS_FILE, "r") as f:
        return json.load(f)


def save_clients(clients: dict):
    with open(CLIENTS_FILE, "w") as f:
        json.dump(clients, f, indent=2)


def get_server_public_key() -> str:
    privkey_path = os.path.join(WG_DIR, "server_private.key")
    if not os.path.exists(privkey_path):
        return ""
    privkey = open(privkey_path).read().strip()
    return _run(f"echo '{privkey}' | wg pubkey")


def get_server_endpoint() -> str:
    try:
        return _run("curl -s4 ifconfig.me")
    except Exception:
        return "YOUR_SERVER_IP"


def next_client_ip() -> str:
    clients = load_clients()
    network = ipaddress.ip_network(SUBNET)
    used_ips = {c["ip"] for c in clients.values()}
    used_ips.add(str(list(network.hosts())[0]))  # server uses .1

    for host in list(network.hosts())[1:]:
        if str(host) not in used_ips:
            return str(host)
    raise RuntimeError("No available IPs in subnet")


def add_client(name: str) -> dict:
    clients = load_clients()
    if name in clients:
        raise ValueError(f"Client '{name}' already exists")

    client_privkey, client_pubkey = generate_keypair()
    psk = generate_psk()
    client_ip = next_client_ip()

    server_pubkey = get_server_public_key()
    endpoint = get_server_endpoint()

    client_conf = f"""[Interface]
PrivateKey = {client_privkey}
Address = {client_ip}/32
DNS = {DNS}
MTU = 1280

[Peer]
PublicKey = {server_pubkey}
PresharedKey = {psk}
Endpoint = {endpoint}:{SERVER_PORT}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"""

    peer_block = f"""
# {name}
[Peer]
PublicKey = {client_pubkey}
PresharedKey = {psk}
AllowedIPs = {client_ip}/32
"""

    wg_conf_path = os.path.join(WG_DIR, f"{WG_INTERFACE}.conf")
    with open(wg_conf_path, "a") as f:
        f.write(peer_block)

    conf_path = os.path.join(WG_DIR, f"client_{name}.conf")
    with open(conf_path, "w") as f:
        f.write(client_conf)
    os.chmod(conf_path, 0o600)

    subprocess.run(
        f"wg set {WG_INTERFACE} peer {client_pubkey} preshared-key <(echo '{psk}') allowed-ips {client_ip}/32",
        shell=True, executable="/bin/bash",
    )

    clients[name] = {
        "ip": client_ip,
        "public_key": client_pubkey,
        "psk": psk,
        "conf": client_conf,
        "created": _run("date -Iseconds"),
    }
    save_clients(clients)

    return {"name": name, "ip": client_ip, "config": client_conf}


def remove_client(name: str) -> bool:
    clients = load_clients()
    if name not in clients:
        return False

    pubkey = clients[name]["public_key"]
    subprocess.run(f"wg set {WG_INTERFACE} peer {pubkey} remove", shell=True)

    del clients[name]
    save_clients(clients)

    conf_path = os.path.join(WG_DIR, f"client_{name}.conf")
    if os.path.exists(conf_path):
        os.remove(conf_path)

    rebuild_server_config(clients)
    return True


def rebuild_server_config(clients: dict):
    privkey = open(os.path.join(WG_DIR, "server_private.key")).read().strip()
    server_ip = str(list(ipaddress.ip_network(SUBNET).hosts())[0])

    conf = f"""[Interface]
PrivateKey = {privkey}
Address = {server_ip}/24
ListenPort = {SERVER_PORT}
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
"""

    for name, c in clients.items():
        conf += f"""
# {name}
[Peer]
PublicKey = {c['public_key']}
PresharedKey = {c['psk']}
AllowedIPs = {c['ip']}/32
"""

    wg_conf_path = os.path.join(WG_DIR, f"{WG_INTERFACE}.conf")
    with open(wg_conf_path, "w") as f:
        f.write(conf)
    os.chmod(wg_conf_path, 0o600)


def list_clients() -> list[dict]:
    clients = load_clients()
    result = []
    for name, c in clients.items():
        result.append({
            "name": name,
            "ip": c["ip"],
            "public_key": c["public_key"],
            "created": c.get("created", ""),
        })
    return result


def get_client_config(name: str) -> str | None:
    clients = load_clients()
    if name in clients:
        return clients[name].get("conf")
    return None
