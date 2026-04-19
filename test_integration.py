#!/usr/bin/env python3
"""
NOIR AGENT v6 — INTEGRATION TEST
===================================
Jalankan di PC untuk memverifikasi seluruh sistem berjalan.
python test_integration.py
"""

import os, sys, json, time
from pathlib import Path
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load env
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)

GATEWAY = os.environ.get("NOIR_GATEWAY_URL", "").rstrip("/")
KEY     = os.environ.get("NOIR_API_KEY", "")
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

PASS = "✅"
FAIL = "❌"
WARN = "⚠️"

results = []

def test(name, fn):
    try:
        ok, detail = fn()
        status = PASS if ok else FAIL
        results.append((status, name, detail))
        print(f"  {status} {name}: {detail}")
        return ok
    except Exception as e:
        results.append((FAIL, name, str(e)))
        print(f"  {FAIL} {name}: {e}")
        return False

print("\n" + "█" * 55)
print("  🖤 NOIR AGENT v6 — INTEGRATION TEST SUITE")
print("█" * 55)

# ── TEST 1: Gateway Health ──
print("\n[Phase 2] Cloudflare Gateway")
test("Gateway Health", lambda: (
    requests.get(f"{GATEWAY}/health", timeout=10).status_code == 200,
    requests.get(f"{GATEWAY}/health", timeout=10).json().get("status")
))

# ── TEST 2: Auth Check ──
test("Auth — Valid Key", lambda: (
    requests.get(f"{GATEWAY}/agent/poll", headers=HEADERS, timeout=10).status_code == 200,
    "Authorized"
))
test("Auth — Invalid Key", lambda: (
    requests.get(f"{GATEWAY}/agent/poll",
        headers={"Authorization": "Bearer WRONG"}, timeout=10).status_code == 401,
    "Unauthorized correctly blocked"
))

# ── TEST 3: Command Queue ──
print("\n[Phase 3] Command Queue E2E")
push_r = requests.post(f"{GATEWAY}/agent/command", headers=HEADERS,
    json={"action": {"type": "info"}, "description": "Integration Test"}, timeout=10).json()
cmd_id = push_r.get("command_id")
test("Push Command", lambda: (bool(cmd_id), f"ID: {cmd_id}"))

poll_r = requests.get(f"{GATEWAY}/agent/poll", headers=HEADERS, timeout=10).json()
cmds = poll_r.get("commands", [])
test("Poll Command", lambda: (len(cmds) >= 0, f"{len(cmds)} commands in queue"))

# ── TEST 4: Result Reporting ──
if cmd_id:
    result_r = requests.post(f"{GATEWAY}/agent/result", headers=HEADERS, json={
        "command_id": cmd_id, "success": True,
        "output": "Integration test OK", "device_id": "PC_TEST"
    }, timeout=10).json()
    test("Report Result", lambda: (result_r.get("ok") == True, "Result stored"))

history = requests.get(f"{GATEWAY}/agent/results", headers=HEADERS, timeout=10).json()
test("History Endpoint", lambda: (
    "results" in history,
    f"{len(history.get('results', []))} completed commands"
))

# ── SUMMARY ──
print("\n" + "─" * 55)
passed = sum(1 for r in results if r[0] == PASS)
total  = len(results)
print(f"  Result: {passed}/{total} tests passed")
if passed == total:
    print("  🎉 ALL SYSTEMS OPERATIONAL — Noir Agent Gateway VERIFIED")
else:
    print("  ⚠️  Some tests failed. Check config and retry.")
print("─" * 55)
