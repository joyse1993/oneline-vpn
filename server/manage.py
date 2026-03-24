#!/usr/bin/env python3
"""Oneline VPN — Client management CLI."""

import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from wg_manager import add_client, remove_client, list_clients, get_client_config
except ImportError:
    sys.path.insert(0, "/usr/local/bin")
    from wg_manager import add_client, remove_client, list_clients, get_client_config

CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
RED = "\033[0;31m"
NC = "\033[0m"


def cmd_add(name: str):
    try:
        result = add_client(name)
        print(f"\n{GREEN}[+] Client '{name}' created!{NC}")
        print(f"  IP: {result['ip']}")
        print(f"\n  Config saved to: /etc/wireguard/client_{name}.conf")
        print(f"\n{CYAN}─── Client Config ───{NC}\n")
        print(result["config"])

        conf_path = f"/etc/wireguard/client_{name}.conf"
        print(f"\n{CYAN}─── QR Code (scan with WireGuard app) ───{NC}\n")
        subprocess.run(f"qrencode -t ansiutf8 < {conf_path}", shell=True)
    except Exception as e:
        print(f"{RED}Error: {e}{NC}")
        sys.exit(1)


def cmd_remove(name: str):
    if remove_client(name):
        print(f"{GREEN}[+] Client '{name}' removed{NC}")
    else:
        print(f"{RED}Client '{name}' not found{NC}")
        sys.exit(1)


def cmd_list():
    clients = list_clients()
    if not clients:
        print("No clients configured")
        return
    print(f"\n{CYAN}{'Name':<20} {'IP':<16} {'Created':<24}{NC}")
    print("─" * 60)
    for c in clients:
        print(f"{c['name']:<20} {c['ip']:<16} {c.get('created', 'N/A'):<24}")
    print(f"\nTotal: {len(clients)} client(s)")


def cmd_config(name: str):
    config = get_client_config(name)
    if config:
        print(config)
    else:
        print(f"{RED}Client '{name}' not found{NC}")
        sys.exit(1)


def cmd_qr(name: str):
    conf_path = f"/etc/wireguard/client_{name}.conf"
    if os.path.exists(conf_path):
        subprocess.run(f"qrencode -t ansiutf8 < {conf_path}", shell=True)
    else:
        print(f"{RED}Config file not found for '{name}'{NC}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print(f"""
{CYAN}Oneline VPN Management{NC}

Usage:
  {sys.argv[0]} add <name>       Add new client
  {sys.argv[0]} remove <name>    Remove client
  {sys.argv[0]} list             List all clients
  {sys.argv[0]} config <name>    Show client config
  {sys.argv[0]} qr <name>        Show QR code for mobile
""")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "add" and len(sys.argv) >= 3:
        cmd_add(sys.argv[2])
    elif cmd == "remove" and len(sys.argv) >= 3:
        cmd_remove(sys.argv[2])
    elif cmd == "list":
        cmd_list()
    elif cmd == "config" and len(sys.argv) >= 3:
        cmd_config(sys.argv[2])
    elif cmd == "qr" and len(sys.argv) >= 3:
        cmd_qr(sys.argv[2])
    else:
        print(f"{RED}Unknown command: {cmd}{NC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
