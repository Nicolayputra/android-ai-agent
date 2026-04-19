#!/usr/bin/env python3
import os, sys, subprocess

def setup_vps():
    print("🧠 [NOIR BRAIN] Initializing Sovereign VPS Environment...")
    
    # 1. Sync .env
    if not os.path.exists(".env"):
        print("⚠️ .env missing. Generating from template...")
        with open(".env", "w") as f:
            f.write("NOIR_GATEWAY_URL=https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev\n")
            f.write("NOIR_API_KEY=NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026\n")
            f.write("NOIR_DEVICE_ID=REDMI_NOTE_14\n")
            f.write("# Masukkan API Key di bawah ini untuk mengaktifkan AI\n")
            f.write("GEMINI_API_KEY=\n")
            f.write("GROQ_API_KEY=\n")

    # 2. Launch Docker
    print("🐳 Launching Containers...")
    subprocess.run("docker-compose up -d --build", shell=True)
    
    print("\n✅ VPS Brain is now ACTIVE.")
    print("🔗 Dashboard accessible at: http://YOUR_VPS_IP:8765")

if __name__ == "__main__":
    setup_vps()
