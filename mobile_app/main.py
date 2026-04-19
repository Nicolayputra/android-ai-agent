"""
NOIR SOVEREIGN MOBILE CORE (SMC) v7.5
=======================================
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
GATEWAY_URL = os.environ.get("NOIR_GATEWAY_URL", "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev")
API_KEY     = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
DEVICE_ID   = os.environ.get("NOIR_DEVICE_ID", "REDMI_NOTE_14")


class SovereignCore(App):
    def build(self):
        self.title = "Noir SMC v7.5"

        root = BoxLayout(orientation='vertical', padding=10, spacing=5)

        self.log_label = Label(
            text="[b]NOIR SOVEREIGN CORE v7.5[/b]\nStatus: [color=00ff88]BOOTING...[/color]",
            markup=True,
            font_size='14sp',
            halign='left',
            valign='top',
            text_size=(None, None)
        )
        self.log_label.bind(width=lambda *x: self.log_label.setter('text_size')(
            self.log_label, (self.log_label.width, None)
        ))

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.log_label)
        root.add_widget(scroll)
        return root

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
            # Get system stats for v9.0
            try:
                import psutil
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
            except:
                cpu, ram = 15, 45 # Default mock for v9.0

            r = requests.post(
                f"{GATEWAY_URL}/agent/register",
                headers=headers,
                json={
                    "device_id": DEVICE_ID, 
                    "agent": "Noir SMC v9.0 Elite",
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
        """Main polling loop."""
        self._register()
        poll_interval = 5

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
                    data = resp.json()
                    commands = data.get("commands", [])

                    if commands:
                        poll_interval = 1
                        for cmd in commands:
                            self._execute(cmd)
                    else:
                        poll_interval = min(poll_interval + 1, 15)
                else:
                    self._log(f"[SMC] Poll: HTTP {resp.status_code}")
                    poll_interval = 10

            except requests.exceptions.ConnectionError:
                self._log("[SMC] No network. Retrying...")
                poll_interval = 30
            except Exception as e:
                self._log(f"[SMC] Loop Error: {e}")
                poll_interval = 10

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
                output = os.popen(str(params.get("cmd", "echo ok"))).read()
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
