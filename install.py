#!/usr/bin/env python3
"""
NOIR AGENT v6 — INSTALL SCRIPT (Termux/Android)
================================================
Jalankan satu kali di Termux untuk setup penuh.
Usage: python install.py
"""

import subprocess, sys, os
from pathlib import Path

PACKAGES_APT = ["python", "git", "curl", "termux-api"]
PACKAGES_PIP = ["requests", "python-dotenv"]

def run(cmd):
    print(f"  → {cmd}")
    r = subprocess.run(cmd, shell=True, text=True)
    return r.returncode == 0

def main():
    print("🖤 NOIR AGENT v6 — INSTALLER")
    print("=" * 40)

    print("\n[1/4] Update repositori Termux...")
    run("pkg update -y")

    print("\n[2/4] Install paket sistem...")
    for pkg in PACKAGES_APT:
        ok = run(f"pkg install -y {pkg}")
        status = "✅" if ok else "⚠️ (gagal, lanjut)"
        print(f"  {status} {pkg}")

    print("\n[3/4] Install library Python...")
    run("pip install --upgrade pip")
    for lib in PACKAGES_PIP:
        ok = run(f"pip install {lib}")
        status = "✅" if ok else "⚠️"
        print(f"  {status} {lib}")

    print("\n[4/4] Periksa file konfigurasi...")
    env_file = Path(".env")
    if not env_file.exists():
        print("  ⚠️  File .env belum ada. Buat dari .env.example:")
        print("       cp .env.example .env")
        print("       nano .env  # Isi API Key dan URL Gateway")
    else:
        print("  ✅ .env ditemukan.")

    print("\n" + "=" * 40)
    print("✅ Instalasi selesai!")
    print("   Jalankan agent dengan: python noir-core/agent.py")

if __name__ == "__main__":
    main()
