#!/usr/bin/env python3
"""
NOIR AGENT v13.0 ELITE-SOVEREIGN — PC DASHBOARD
=============================================
Command Center: kirim perintah, lihat histori, monitor status.
Jalankan di PC: python noir-ui/dashboard.py
"""

import os, json, time, sys
from pathlib import Path
from datetime import datetime

# Load env dari root proyek
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

try:
    import requests
except ImportError:
    print("❌ Library 'requests' tidak ada. Jalankan: pip install requests")
    sys.exit(1)

GATEWAY = os.environ.get("NOIR_GATEWAY_URL", "").rstrip("/")
API_KEY = os.environ.get("NOIR_API_KEY", "")

if not GATEWAY or not API_KEY:
    print("❌ NOIR_GATEWAY_URL atau NOIR_API_KEY belum diisi di .env")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# ─── HELPER ───
def api(method, endpoint, data=None):
    url = f"{GATEWAY}/{endpoint.lstrip('/')}"
    try:
        r = requests.request(method, url, headers=HEADERS, json=data, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def send_command(action_type, params=None, description=""):
    action = {"type": action_type, **(params or {})}
    return api("POST", "/agent/command", {"action": action, "description": description or action_type})

def show_results(limit=10):
    data = api("GET", "/agent/results")
    results = data.get("results", [])[:limit]
    if not results:
        print("  (belum ada hasil)")
        return
    for r in results:
        result = json.loads(r.get("result") or "{}")
        ts = r.get("updated_at", "?")
        success = "✅" if result.get("success") else "❌"
        output = result.get("output") or result.get("error") or "-"
        print(f"  {success} [{ts[:19]}] {r.get('description','?')}")
        print(f"     → {output[:120]}")

# ─── MAIN DASHBOARD ───
def main():
    print("\n" + "█" * 60)
    print("  🖤 NOIR AGENT v13.0 ELITE-SOVEREIGN — PC DASHBOARD")
    print("  Authority: USER (Absolute Sovereign)")
    print("█" * 60)

    # Cek koneksi
    health = api("GET", "/health")
    if "error" in health:
        print(f"\n❌ Gagal terhubung ke Gateway: {health['error']}")
        sys.exit(1)
    print(f"\n✅ Gateway Online: {health.get('agent')} | {health.get('ts','')[:19]}")

    MENU = {
        "1": ("Screenshot", lambda: send_command("screenshot", description="Screenshot HP")),
        "2": ("Cek Baterai", lambda: send_command("battery", description="Status Baterai")),
        "3": ("Info Agent", lambda: send_command("info", description="Info Noir Agent")),
        "4": ("Custom Shell", None),
        "5": ("Lihat Histori Hasil", None),
        "0": ("Keluar", None),
    }

    while True:
        print("\n─── MENU ───────────────────────────────────")
        for k, (label, _) in MENU.items():
            print(f"  [{k}] {label}")
        print("────────────────────────────────────────────")

        choice = input("Pilih > ").strip()

        if choice == "0":
            print("🔴 Dashboard ditutup.")
            break
        elif choice == "4":
            cmd = input("  Shell command: ").strip()
            if cmd:
                r = send_command("shell", {"cmd": cmd}, description=f"shell: {cmd}")
                print(f"  → {r}")
        elif choice == "5":
            print("\n─── HISTORI HASIL ───")
            show_results()
        elif choice in MENU and MENU[choice][1]:
            r = MENU[choice][1]()
            print(f"  → Terkirim: {r}")
        else:
            print("  ⚠️  Pilihan tidak valid.")

if __name__ == "__main__":
    main()
