"""
NOIR AGENT v14.0 COMMANDER — CORE ENGINE
================================
The Sovereign Android AI Agent.
Host: Redmi Note 14 (Termux)
Brain: VPS Neuro-Center via Cloudflare Gateway
Authority: USER (Absolute)
"""

import os, sys, time, logging, subprocess, json, asyncio
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────
# HARDENED ENV LOADER
# ─────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR  = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

def load_env():
    """Load env vars dari multiple fallback paths."""
    paths = [
        BASE_DIR / ".env",
        Path.home() / ".env",
        Path("/sdcard/Download/noir.env"),
    ]
    for p in paths:
        if p.exists():
            with open(p, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())

load_env()

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
GATEWAY_URL = os.environ.get("NOIR_GATEWAY_URL", "").rstrip("/")
API_KEY     = os.environ.get("NOIR_API_KEY", "")
DEVICE_ID   = os.environ.get("NOIR_DEVICE_ID", "REDMI_NOTE_14")
AGENT_NAME  = "Noir Agent v14.0 COMMANDER"

if not GATEWAY_URL or not API_KEY:
    print("⚠️  FATAL: NOIR_GATEWAY_URL dan NOIR_API_KEY belum dikonfigurasi.")
    print("   Buat file .env di root proyek. Lihat .env.example")
    sys.exit(1)

# ─────────────────────────────────────────
# LOGGING — UTF-8 Hardened
# ─────────────────────────────────────────
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        RotatingFileHandler(LOG_DIR / "noir_agent.log", maxBytes=5*1024*1024, backupCount=2, encoding="utf-8"),
    ],
)
log = logging.getLogger("NoirAgent")

# ─────────────────────────────────────────
# SYSTEM SHELL EXECUTOR
# ─────────────────────────────────────────
def shell(cmd: str, timeout: int = 60) -> dict:
    """Jalankan perintah shell dengan penanganan error penuh."""
    log.info(f"[SHELL] {cmd}")
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=timeout,
            encoding="utf-8", errors="replace"
        )
        return {"success": r.returncode == 0, "output": r.stdout.strip(), "error": r.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": f"Timeout setelah {timeout}s"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}

# ─────────────────────────────────────────
# CLOUD GATEWAY CLIENT
# ─────────────────────────────────────────
async def cloud(method: str, endpoint: str, data: dict = None) -> dict | None:
    """Komunikasi ke Cloudflare Gateway (Asynchronous)."""
    try:
        import aiohttp
        url = f"{GATEWAY_URL}/{endpoint.lstrip('/')}"
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(url, headers=headers, timeout=15) as r:
                    r.raise_for_status()
                    return await r.json()
            else:
                async with session.post(url, headers=headers, json=data, timeout=15) as r:
                    r.raise_for_status()
                    return await r.json()
    except Exception as e:
        log.warning(f"[CLOUD-ERR] {method} /{endpoint} → {e}")
        return None

# ─────────────────────────────────────────
# ACTION EXECUTOR (The Body)
# ─────────────────────────────────────────
class ActionExecutor:
    """Eksekutor aksi Android. Tunduk pada kewenangan USER."""

    ALLOWED_ACTIONS = {"tap", "swipe", "text", "keyevent", "shell", "screenshot", "battery", "info"}

    @staticmethod
    def execute(action: str, params: dict) -> dict:
        if action not in ActionExecutor.ALLOWED_ACTIONS:
            return {"success": False, "error": f"Aksi '{action}' tidak diizinkan oleh Sovereign Authority."}

        log.info(f"⚡ EXECUTE: {action} | {params}")

        if action == "tap":
            return shell(f"input tap {params.get('x', 0)} {params.get('y', 0)}")
        elif action == "swipe":
            return shell(f"input swipe {params.get('x1',0)} {params.get('y1',0)} {params.get('x2',0)} {params.get('y2',0)} {params.get('duration',300)}")
        elif action == "text":
            txt = str(params.get("text", "")).replace(" ", "%s")
            return shell(f"input text '{txt}'")
        elif action == "keyevent":
            return shell(f"input keyevent {params.get('key', 3)}")
        elif action == "shell":
            return shell(params.get("cmd", ""))
        elif action == "screenshot":
            ts = int(time.time())
            path = f"/sdcard/Download/noir_ss_{ts}.png"
            res = shell(f"termux-screenshot -o {path}")
            return {"success": res["success"], "output": f"Screenshot: {path}", "path": path}
        elif action == "battery":
            return shell("termux-battery-status")
        elif action == "info":
            return {"success": True, "output": f"{AGENT_NAME} | Device: {DEVICE_ID} | Online: {datetime.now().isoformat()}"}

        return {"success": False, "error": "Unknown action"}

# ─────────────────────────────────────────
# MAIN LOOP — Adaptive & Self-Healing
# ─────────────────────────────────────────
async def run():
    # Mengunci Termux agar tidak dimatikan Android
    shell("termux-wake-lock")
    
    log.info(f"🖤 {AGENT_NAME} ONLINE — Device: {DEVICE_ID}")
    log.info(f"   Gateway: {GATEWAY_URL}")

    # Registrasi ke Cloud
    reg = await cloud("POST", "/agent/register", {"device_id": DEVICE_ID, "agent": AGENT_NAME})
    if reg:
        log.info(f"✅ Registered: {reg}")

    poll_interval = 2
    while True:
        try:
            data = await cloud("GET", "/agent/poll")
            if data:
                commands = data.get("commands", [])
                if commands:
                    poll_interval = 1  # Turbo mode
                    for cmd in commands:
                        cmd_id  = cmd.get("command_id")
                        action  = cmd.get("action", {})
                        atype   = action.get("type") or action.get("action")
                        params  = action.get("params", action)

                        result = ActionExecutor.execute(atype, params)

                        # Kirim hasil ke cloud
                        await cloud("POST", "/agent/result", {
                            "command_id": cmd_id,
                            "device_id": DEVICE_ID,
                            "success": result["success"],
                            "output": result.get("output", ""),
                            "error": result.get("error", ""),
                        })
                        log.info(f"📤 Result sent: {cmd_id} → {result['success']}")
                else:
                    poll_interval = min(poll_interval + 1, 10)  # Adaptive backoff

            await asyncio.sleep(poll_interval)

        except asyncio.CancelledError:
            log.info("🔴 Noir Agent dihentikan oleh USER.")
            break
        except Exception as e:
            log.error(f"💀 Critical Error: {e}")
            await asyncio.sleep(10)  # Self-healing delay

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        log.info("🔴 Agent shutdown gracefully.")
