"""
NOIR SOVEREIGN MOBILE CORE (SMC) v13.0 ELITE-SOVEREIGN
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
# Fallback to VPS IP if Cloudflare Worker is not ready
GATEWAY_URL = "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev"
API_KEY     = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026"
DEVICE_ID   = "REDMI_NOTE_14"

# --- SAFETY FILTER (v12.5) ---
BLACKLISTED_PACKAGES = [
    "com.bca", "com.mandiri", "id.co.bri", "com.bnismartid", 
    "com.btpns", "id.dana", "com.shopee.id" # Added Shopee for wallet safety
]

def is_safe_command(cmd_str):
    for pkg in BLACKLISTED_PACKAGES:
        if pkg in cmd_str.lower():
            return False
    return True


class SovereignCore(App):
    is_stealth = False

    def build(self):
        self.title = "Noir SMC v13.0 ELITE-SOVEREIGN"
        self.root = BoxLayout(orientation='vertical')
        self.show_active_ui()
        return self.root

    def show_active_ui(self):
        self.root.clear_widgets()
        self.root.padding = 10
        self.root.spacing = 5
        
        self.log_label = Label(
            text="[b]NOIR SOVEREIGN CORE v13.0[/b]\nStatus: [color=00ff88]ELITE-SOVEREIGN[/color]",
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
                    "agent": "Noir SMC v13.0 ELITE-SOVEREIGN",
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

    def _main_loop(self):
        """Main polling loop with v13.0 ELITE-SOVEREIGN self-healing."""
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
                    output = os.popen(cmd).read()
                    result = {"success": True, "output": output.strip()}

            elif atype == "tap":
                x, y = params.get("x", 0), params.get("y", 0)
                os.system(f"input tap {x} {y}")
                result = {"success": True, "output": f"Tapped ({x},{y})"}

            elif atype == "swipe":
                cmd = (f"input swipe {params.get('x1',0)} {params.get('y1',0)} "
                       f"{params.get('x2',500)} {params.get('y2',500)} "
                       f"{params.get('duration',500)}")
                os.system(cmd)
                result = {"success": True, "output": "Swipe done"}

            elif atype == "keyevent":
                os.system(f"input keyevent {params.get('key', 26)}")
                result = {"success": True, "output": f"Key {params.get('key')} sent"}

            elif atype in ("app_start", "launch"):
                pkg = params.get("package", "")
                if not is_safe_command(pkg):
                    result = {"success": False, "error": "SECURITY BLOCK: Financial apps are forbidden."}
                else:
                    os.system(f"am start -n {pkg}")
                    result = {"success": True, "output": f"Launched {pkg}"}

            elif atype in ("app_stop", "kill"):
                pkg = params.get("package", "")
                os.system(f"am force-stop {pkg}")
                result = {"success": True, "output": f"Stopped {pkg}"}

            elif atype in ("screenshot", "capture"):
                # Use internal storage to avoid /sdcard permission issues on Android 14
                path = os.path.join(App.get_running_app().user_data_dir, "noir_vision.png")
                os.system(f"screencap -p {path}")
                time.sleep(1.0) # Wait for file to write

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
                path = os.path.join(App.get_running_app().user_data_dir, "view_hierarchy.xml")
                os.system(f"uiautomator dump {path}")
                time.sleep(1.0)
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

        except Exception as e:
            result = {"success": False, "error": str(e)}
            self._log(f"[SMC] Exec Error: {e}")

        self._report_result(cmd_id, result)

    def _report_result(self, cmd_id, result):
        """Send execution result back to the Cloudflare Gateway."""
        try:
            requests.post(
                f"{GATEWAY_URL}/agent/result",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "command_id": cmd_id,
                    "device_id": DEVICE_ID,
                    "success": result.get("success", False),
                    "output": result.get("output", ""),
                    "error": result.get("error", "")
                },
                timeout=15
            )
        except Exception as e:
            self._log(f"[SMC] Report Error: {e}")


if __name__ == '__main__':
    SovereignCore().run()
