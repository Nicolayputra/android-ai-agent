#!/data/data/com.termux/files/usr/bin/bash
# NOIR AGENT v6 — TERMUX AUTO SETUP
# Salin file ini ke /sdcard/Download/noir-agent/ lalu:
# termux-open-url file:///sdcard/Download/noir-agent/termux_setup.sh
# ATAU jalankan langsung di Termux: bash /sdcard/Download/noir-agent/termux_setup.sh

echo "================================"
echo "  NOIR AGENT v6 — Termux Setup"
echo "================================"

# 1. Update & Install
echo "[1/5] Updating Termux..."
pkg update -y -q 2>&1 | tail -3

echo "[2/5] Installing packages..."
pkg install -y python git termux-api 2>&1 | tail -3

echo "[3/5] Installing Python libraries..."
pip install requests python-dotenv -q 2>&1

echo "[4/5] Copying files to Termux home..."
mkdir -p ~/noir-agent/noir-core ~/noir-agent/logs
cp /sdcard/Download/noir-agent/noir-core/agent.py ~/noir-agent/noir-core/
cp /sdcard/Download/noir-agent/.env ~/noir-agent/.env
cp /sdcard/Download/noir-agent/install.py ~/noir-agent/install.py

echo "[5/5] Creating startup alias..."
echo 'alias noir="cd ~/noir-agent && python noir-core/agent.py"' >> ~/.bashrc
echo 'alias noir-log="tail -f ~/noir-agent/logs/noir_agent.log"' >> ~/.bashrc

echo ""
echo "================================"
echo "  SETUP SELESAI!"
echo "  Jalankan: cd ~/noir-agent && python noir-core/agent.py"
echo "  Atau ketik: noir"
echo "================================"
