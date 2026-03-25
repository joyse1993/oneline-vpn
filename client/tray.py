"""19 VPN Client — macOS menu bar (tray) icon using rumps."""

try:
    import rumps
except ImportError:
    rumps = None

from config import list_profiles, load_config, save_config, APP_NAME, APP_VERSION
from vpn_engine import VPNEngine


class NineteenVPNTray:
    """Menu bar app for 19 VPN on macOS."""

    def __init__(self):
        self.engine = VPNEngine()

        if rumps is None:
            print("rumps not installed. Install with: pip install rumps")
            print("Running in CLI mode instead.")
            return

        self.app = rumps.App(
            APP_NAME,
            title="🛡 19 VPN",
            quit_button=None,
        )
        self._build_menu()

    def _build_menu(self):
        profiles = list_profiles()
        config = load_config()
        status = self.engine.get_status()

        items = []

        if status["connected"]:
            items.append(rumps.MenuItem(
                f"● Connected: {status.get('profile', 'Unknown')}",
                callback=None,
            ))
            items.append(rumps.separator)
            items.append(rumps.MenuItem(
                f"  ↓ {status.get('transfer_rx', 'N/A')}  ↑ {status.get('transfer_tx', 'N/A')}",
                callback=None,
            ))
            if status.get("endpoint"):
                items.append(rumps.MenuItem(f"  Server: {status['endpoint']}", callback=None))
            items.append(rumps.separator)
            items.append(rumps.MenuItem("Disconnect", callback=self._disconnect))
        else:
            items.append(rumps.MenuItem("○ Disconnected", callback=None))
            items.append(rumps.separator)

            if profiles:
                connect_menu = rumps.MenuItem("Connect")
                for p in profiles:
                    connect_menu[p] = rumps.MenuItem(p, callback=self._make_connect(p))
                items.append(connect_menu)
            else:
                items.append(rumps.MenuItem("No profiles — import one below", callback=None))

        items.append(rumps.separator)

        kill_switch = rumps.MenuItem("Kill Switch", callback=self._toggle_kill_switch)
        kill_switch.state = 1 if config.get("kill_switch") else 0
        items.append(kill_switch)

        auto_connect = rumps.MenuItem("Auto-Connect on Launch", callback=self._toggle_auto_connect)
        auto_connect.state = 1 if config.get("auto_connect") else 0
        items.append(auto_connect)

        items.append(rumps.separator)
        items.append(rumps.MenuItem("Import Profile...", callback=self._import_profile))
        items.append(rumps.MenuItem("Refresh", callback=self._refresh))
        items.append(rumps.separator)
        items.append(rumps.MenuItem(f"19 VPN v{APP_VERSION}", callback=None))
        items.append(rumps.MenuItem("Quit", callback=self._quit))

        self.app.menu.clear()
        for item in items:
            self.app.menu.add(item)

        self.app.title = "🛡" if not status["connected"] else "🛡●"

    def _make_connect(self, profile_name: str):
        def callback(_):
            success, msg = self.engine.connect(profile_name)
            if success:
                rumps.notification(APP_NAME, "Connected", f"Profile: {profile_name}")
                config = load_config()
                config["active_profile"] = profile_name
                save_config(config)
            else:
                rumps.notification(APP_NAME, "Connection Failed", msg)
            self._build_menu()
        return callback

    def _disconnect(self, _):
        success, msg = self.engine.disconnect()
        if success:
            rumps.notification(APP_NAME, "Disconnected", "VPN connection closed")
        else:
            rumps.notification(APP_NAME, "Error", msg)
        self._build_menu()

    def _toggle_kill_switch(self, sender):
        config = load_config()
        config["kill_switch"] = not config.get("kill_switch", False)
        save_config(config)
        sender.state = 1 if config["kill_switch"] else 0

        if config["kill_switch"] and self.engine.connected:
            self.engine._enable_kill_switch()
            rumps.notification(APP_NAME, "Kill Switch", "Enabled — traffic blocked if VPN drops")
        elif not config["kill_switch"]:
            self.engine._disable_kill_switch()
            rumps.notification(APP_NAME, "Kill Switch", "Disabled")

    def _toggle_auto_connect(self, sender):
        config = load_config()
        config["auto_connect"] = not config.get("auto_connect", False)
        save_config(config)
        sender.state = 1 if config["auto_connect"] else 0

    def _import_profile(self, _):
        response = rumps.Window(
            message="Paste your WireGuard config:",
            title="Import VPN Profile",
            default_text="",
            ok="Import",
            cancel="Cancel",
            dimensions=(420, 220),
        ).run()

        if response.clicked:
            text = response.text.strip()
            if "[Interface]" in text and "[Peer]" in text:
                name_resp = rumps.Window(
                    message="Name this profile:",
                    title="Profile Name",
                    default_text="19vpn",
                    ok="Save",
                    cancel="Cancel",
                ).run()
                if name_resp.clicked and name_resp.text.strip():
                    from config import save_profile
                    name = name_resp.text.strip().replace(" ", "-")
                    save_profile(name, text)
                    rumps.notification(APP_NAME, "Profile Imported", name)
                    self._build_menu()
            else:
                rumps.notification(APP_NAME, "Invalid Config", "Must contain [Interface] and [Peer]")

    def _refresh(self, _):
        self._build_menu()

    def _quit(self, _):
        if self.engine.connected:
            self.engine.disconnect()
        rumps.quit_application()

    def run(self):
        if rumps is None:
            print(f"\n◆ {APP_NAME} v{APP_VERSION}")
            print("=" * 44)
            print("GUI requires 'rumps'. Install:")
            print("  pip install rumps")
            print("\nRunning CLI fallback...")
            self._cli_mode()
        else:
            config = load_config()
            if config.get("auto_connect") and config.get("active_profile"):
                profile = config["active_profile"]
                if profile in list_profiles():
                    success, _ = self.engine.connect(profile)
                    if success:
                        self._build_menu()
            self.app.run()

    def _cli_mode(self):
        while True:
            status = self.engine.get_status()
            profiles = list_profiles()

            state = "● Connected" if status["connected"] else "○ Disconnected"
            print(f"\n{state}")
            if status["connected"]:
                print(f"  Profile: {status.get('profile', 'N/A')}")
                print(f"  ↓ {status.get('transfer_rx', 'N/A')}  ↑ {status.get('transfer_tx', 'N/A')}")

            print(f"\nProfiles: {', '.join(profiles) if profiles else 'none'}")
            print("\nCommands: connect <name> | disconnect | status | quit")

            try:
                cmd = input("\n19vpn> ").strip().split()
            except (KeyboardInterrupt, EOFError):
                break

            if not cmd:
                continue
            elif cmd[0] == "quit":
                if self.engine.connected:
                    self.engine.disconnect()
                break
            elif cmd[0] == "connect" and len(cmd) >= 2:
                ok, msg = self.engine.connect(cmd[1])
                print(msg)
            elif cmd[0] == "disconnect":
                ok, msg = self.engine.disconnect()
                print(msg)
            elif cmd[0] == "status":
                pass
            else:
                print("Unknown command")
