# Oneline VPN — Platform Setup Guide

## macOS

### Option A: Oneline VPN Client (Recommended)
1. Install the client: `cd client && pip install -r requirements.txt && python nexusvpn.py`
2. Click the Oneline VPN icon in the menu bar
3. Click **Import Profile** and paste your config from the dashboard
4. Click **Connect** → select your profile

### Option B: WireGuard App
1. Install WireGuard: `brew install wireguard-tools` or download from [wireguard.com](https://www.wireguard.com/install/)
2. Download your `.conf` file from the dashboard
3. Import: `sudo wg-quick up /path/to/your-config.conf`
4. To disconnect: `sudo wg-quick down /path/to/your-config.conf`

---

## Windows

1. Download WireGuard from [wireguard.com/install](https://www.wireguard.com/install/)
2. Open the WireGuard app
3. Click **Import tunnel(s) from file**
4. Select the `.conf` file you downloaded from the Oneline VPN dashboard
5. Click **Activate** to connect

---

## Android

1. Install **WireGuard** from [Google Play](https://play.google.com/store/apps/details?id=com.wireguard.android)
2. Open the WireGuard app
3. Tap the **+** button → **Scan from QR code**
4. Open your Oneline VPN dashboard on a computer, click **View Config** on your device
5. Scan the QR code with your phone's camera
6. Give the tunnel a name (e.g., "Oneline VPN") and tap **Create Tunnel**
7. Toggle the switch to connect

---

## iOS

1. Install **WireGuard** from the [App Store](https://apps.apple.com/app/wireguard/id1441195209)
2. Open the WireGuard app
3. Tap **Add a tunnel** → **Create from QR code**
4. Open your Oneline VPN dashboard on a computer, click **View Config** on your device
5. Scan the QR code with your phone's camera
6. Tap **Allow** when prompted to add VPN configuration
7. Toggle the switch to connect

---

## Troubleshooting

### Connection issues
- Make sure your VPN server is running: `sudo wg show` on the server
- Check that port **51820/UDP** is open in your firewall
- Try changing DNS to `8.8.8.8` or `9.9.9.9` if some sites don't load

### Slow speed
- Check server load: `htop` on the VPS
- Try a VPS closer to your location
- Increase MTU from 1280 to 1420 (in the config `[Interface]` section)

### ISP blocking
- If your ISP blocks WireGuard, the server setup includes obfuscation (wstunnel)
- This wraps WireGuard traffic in WebSocket, making it look like normal HTTPS
