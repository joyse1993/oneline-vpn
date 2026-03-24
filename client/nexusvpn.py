#!/usr/bin/env python3
"""
Oneline VPN — macOS Desktop Client v2.0
Menu bar app with WireGuard integration.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_NAME, APP_VERSION, ensure_dirs
from tray import OnelineTray


def main():
    ensure_dirs()
    print(f"◆ {APP_NAME} v{APP_VERSION}")
    print("Starting...")

    app = OnelineTray()
    app.run()


if __name__ == "__main__":
    main()
