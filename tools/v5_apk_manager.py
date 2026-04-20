"""
V5 APK MANAGER - EXPERT COMMAND CENTER
=======================================
Mengelola instalasi, startup, dan monitoring Sovereign Mobile Core (SMC).
"""

import os, sys, subprocess, time

ADB = r"c:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent\adb_tools\platform-tools\adb.exe"
APK_PATH = "mobile_app/bin/sovereigncore-0.1-debug.apk" # Path default buildozer
PACKAGE = "org.antigravity.sovereigncore"

def run_adb(cmd):
    return subprocess.run(f"{ADB} {cmd}", shell=True, capture_output=True, text=True)

def install_apk():
    print(f"🚀 Memasang SMC v5.0 ke perangkat...")
    if not os.path.exists(APK_PATH):
        print(f"❌ File APK tidak ditemukan di {APK_PATH}. Pastikan Anda sudah menjalankan build.")
        return
    res = run_adb(f"install -r {APK_PATH}")
    print(res.stdout)

def start_agent():
    print(f"🔥 Menjalankan Sovereign Core...")
    # Jalankan Main Activity
    run_adb(f"shell am start -n {PACKAGE}/org.kivy.android.PythonActivity")
    # Jalankan Service di latar belakang
    run_adb(f"shell am startservice {PACKAGE}/.SovereignEngine")

def monitor_logs():
    print(f"📋 Monitoring log SMC (Ctrl+C untuk berhenti)...")
    subprocess.run(f"{ADB} logcat -s python", shell=True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python v5_apk_manager.py [install|start|log]")
    else:
        cmd = sys.argv[1]
        if cmd == "install": install_apk()
        elif cmd == "start": start_agent()
        elif cmd == "log": monitor_logs()
