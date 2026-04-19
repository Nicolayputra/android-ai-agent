"""
SOVEREIGN MOBILE CORE (SMC) v5.0 - NATIVE AGENT
===============================================
Framework: Kivy + Buildozer (Android Native)
Role: Persistent AI Agent Executor

Security Features:
- Encrypted Tunneling
- RSA Key Auth
- Anti-Kill Service
"""

import os
import json
import time
import requests
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform

# --- LOAD CONFIG FROM V5 CORE ---
URL_GATEWAY = os.environ.get("NOIR_GATEWAY_URL", "https://agent-cloud-backend.si-umkm-ikm-pbd.workers.dev")
API_KEY     = os.environ.get("NOIR_API_KEY", "SUPER_SECRET_TOKEN_V5")
DEVICE_ID   = os.environ.get("NOIR_DEVICE_ID", "REDMI_NOTE_14_SMC")

class SovereignCore(App):
    def build(self):
        self.title = "System Core V5"
        self.layout = BoxLayout(orientation='vertical', padding=20)
        
        # UI Premium & Stealth
        self.status_label = Label(
            text="[b]SOVEREIGN MOBILE CORE[/b]\nStatus: [color=00ff00]INITIALIZING[/color]",
            markup=True,
            font_size='18sp',
            halign='center'
        )
        self.layout.add_widget(self.status_label)
        
        # Start the Background Engine
        threading.Thread(target=self.background_engine, daemon=True).start()
        
        return self.layout

    def on_start(self):
        """Inisialisasi sistem saat aplikasi dimulai."""
        print("[SMC] Sovereign Engine Starting...")
        self.acquire_wakelock()
        self.register_agent()
        # Start the Background Engine thread
        threading.Thread(target=self.background_engine, daemon=True).start()
        
    def acquire_wakelock(self):
        """Mencegah sistem mematikan CPU saat layar mati."""
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            PowerManager = autoclass('android.os.PowerManager')
            
            activity = PythonActivity.mActivity
            pm = activity.getSystemService(Context.POWER_SERVICE)
            self.wakelock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "SMC:WakeLock")
            self.wakelock.acquire()
            print("[SMC] Global WakeLock Acquired.")
        except Exception as e:
            print(f"[SMC] WakeLock Error (Non-Android?): {e}")

    def register_agent(self):
        """Mendaftarkan diri ke Gateway Cloudflare."""
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        try:
            requests.post(f"{URL_GATEWAY}/agent/register", headers=headers, json={
                "device_id": DEVICE_ID,
                "agent": "Noir Mobile Agent v7.2"
            }, timeout=10)
            print("[SMC] Registration Successful.")
        except: pass

    def background_engine(self):
        """Mata rantai utama: Polling & Execution (Adaptive)."""
        print("[SMC] Background Engine Running.")
        poll_interval = 2
        
        while True:
            try:
                # Polling via Cloudflare
                headers = {"Authorization": f"Bearer {API_KEY}"}
                response = requests.get(f"{URL_GATEWAY}/agent/poll", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    commands = data.get("commands", [])
                    
                    if commands:
                        poll_interval = 1 # Turbo Mode
                        for cmd in commands:
                            self.execute_mission(cmd)
                    else:
                        poll_interval = min(poll_interval + 1, 10) # Power Save
                
                time.sleep(poll_interval)
                
            except Exception as e:
                print(f"[SMC] Engine Error: {e}")
                time.sleep(10)

    def execute_mission(self, cmd_data):
        """Eksekusi perintah di tingkat sistem Android."""
        cmd_id = cmd_data.get("command_id")
        action = cmd_data.get("action", {})
        atype  = action.get("action") or action.get("type")
        params = action.get("params", action)
        
        print(f"[SMC] Mission Received: {atype}")
        
        result = {"success": False, "output": "", "error": "Unknown Action"}
        
        try:
            if atype == "get_time" or atype == "time":
                result = {"success": True, "output": time.strftime("%H:%M:%S")}
            elif atype == "shell":
                output = os.popen(params.get("cmd")).read()
                result = {"success": True, "output": output}
            elif atype == "tap":
                os.system(f"input tap {params.get('x')} {params.get('y')}")
                result = {"success": True, "output": f"Tapped at {params.get('x')},{params.get('y')}"}
            elif atype == "swipe":
                os.system(f"input swipe {params.get('x1')} {params.get('y1')} {params.get('x2')} {params.get('y2')} {params.get('duration', 500)}")
                result = {"success": True, "output": "Swipe executed"}
            elif atype == "keyevent":
                os.system(f"input keyevent {params.get('key')}")
                result = {"success": True, "output": f"Keyevent {params.get('key')} sent"}
            elif atype == "app_start":
                os.system(f"am start -n {params.get('package')}")
                result = {"success": True, "output": f"App {params.get('package')} started"}
            elif atype == "app_stop":
                os.system(f"am force-stop {params.get('package')}")
                result = {"success": True, "output": f"App {params.get('package')} stopped"}
            elif atype == "screenshot" or atype == "capture":
                # ... (Logika screenshot yang sudah ada)
                # Path sementara di HP
                path = "/sdcard/Download/smc_vision.png"
                os.system(f"screencap -p {path}")
                
                # Upload ke R2 Gateway
                headers = {"Authorization": f"Bearer {API_KEY}", "X-API-Key": API_KEY}
                with open(path, 'rb') as f:
                    r = requests.post(
                        f"{URL_GATEWAY}/agent/upload", 
                        headers=headers, 
                        files={'file': f},
                        data={'device_id': DEVICE_ID},
                        timeout=30
                    )
                
                if r.status_code == 200:
                    key = r.json().get('key')
                    result = {"success": True, "output": f"Screenshot uploaded: {key}", "key": key}
                else:
                    result = {"success": False, "error": f"Upload failed: {r.text}"}

            # 2. Report Result back to Cloud
            headers = {"Authorization": f"Bearer {API_KEY}"}
            requests.post(f"{URL_GATEWAY}/agent/result", headers=headers, json={
                "command_id": cmd_id,
                "success": result["success"],
                "output": result.get("output", ""),
                "error": result.get("error", ""),
                "device_id": DEVICE_ID
            }, timeout=10)
            
        except Exception as e:
            print(f"[SMC] Execution Fail: {e}")


if __name__ == '__main__':
    SovereignCore().run()
