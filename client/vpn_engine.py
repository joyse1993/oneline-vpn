"""NexusVPN Client — WireGuard VPN engine for macOS."""

import subprocess
import os
import re
import time
import threading

from config import PROFILES_DIR, load_config


class VPNEngine:
    def __init__(self):
        self.connected = False
        self.current_profile = None
        self._monitor_thread = None
        self._stop_monitor = False

    @staticmethod
    def is_wireguard_installed() -> bool:
        try:
            subprocess.run(["which", "wg"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def install_wireguard():
        """Install WireGuard via Homebrew if not present."""
        try:
            subprocess.run(["brew", "install", "wireguard-tools"], check=True)
            return True
        except Exception:
            return False

    def connect(self, profile_name: str) -> tuple[bool, str]:
        conf_path = os.path.join(PROFILES_DIR, f"{profile_name}.conf")
        if not os.path.exists(conf_path):
            return False, f"Profile '{profile_name}' not found"

        if not self.is_wireguard_installed():
            return False, "WireGuard not installed. Run: brew install wireguard-tools"

        if self.connected:
            self.disconnect()

        try:
            result = subprocess.run(
                ["sudo", "wg-quick", "up", conf_path],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                self.connected = True
                self.current_profile = profile_name
                self._start_monitor()

                config = load_config()
                if config.get("kill_switch"):
                    self._enable_kill_switch()

                return True, "Connected"
            else:
                return False, result.stderr.strip() or "Connection failed"
        except subprocess.TimeoutExpired:
            return False, "Connection timed out"
        except Exception as e:
            return False, str(e)

    def disconnect(self) -> tuple[bool, str]:
        if not self.connected or not self.current_profile:
            return True, "Not connected"

        self._stop_monitor = True
        conf_path = os.path.join(PROFILES_DIR, f"{self.current_profile}.conf")

        try:
            self._disable_kill_switch()
            result = subprocess.run(
                ["sudo", "wg-quick", "down", conf_path],
                capture_output=True, text=True, timeout=15,
            )
            self.connected = False
            self.current_profile = None
            return True, "Disconnected"
        except Exception as e:
            self.connected = False
            self.current_profile = None
            return False, str(e)

    def get_status(self) -> dict:
        if not self.connected:
            return {"connected": False, "profile": None}

        try:
            result = subprocess.run(
                ["sudo", "wg", "show"],
                capture_output=True, text=True, timeout=5,
            )
            output = result.stdout

            transfer = {"rx": "0 B", "tx": "0 B"}
            rx_match = re.search(r"transfer:\s+([\d.]+\s+\w+)\s+received,\s+([\d.]+\s+\w+)\s+sent", output)
            if rx_match:
                transfer = {"rx": rx_match.group(1), "tx": rx_match.group(2)}

            endpoint = ""
            ep_match = re.search(r"endpoint:\s+(.+)", output)
            if ep_match:
                endpoint = ep_match.group(1)

            return {
                "connected": True,
                "profile": self.current_profile,
                "endpoint": endpoint,
                "transfer_rx": transfer["rx"],
                "transfer_tx": transfer["tx"],
            }
        except Exception:
            return {"connected": self.connected, "profile": self.current_profile}

    def _enable_kill_switch(self):
        """Block all traffic except through the VPN tunnel."""
        rules = [
            "sudo pfctl -E",
            'echo "block all\npass on lo0\npass on utun+\npass out proto udp to any port 51820" | sudo pfctl -f -',
        ]
        for rule in rules:
            subprocess.run(rule, shell=True, capture_output=True)

    def _disable_kill_switch(self):
        subprocess.run("sudo pfctl -d", shell=True, capture_output=True)
        subprocess.run("sudo pfctl -F all", shell=True, capture_output=True)

    def _start_monitor(self):
        self._stop_monitor = False
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def _monitor_loop(self):
        while not self._stop_monitor:
            time.sleep(10)
            if self._stop_monitor:
                break
            try:
                result = subprocess.run(
                    ["sudo", "wg", "show"],
                    capture_output=True, text=True, timeout=5,
                )
                if result.returncode != 0:
                    self.connected = False
            except Exception:
                pass
