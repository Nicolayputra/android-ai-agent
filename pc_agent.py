import os
import time
import requests
import subprocess

GATEWAY_URL = os.environ.get("NOIR_GATEWAY_URL", "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev")
API_KEY     = os.environ.get("NOIR_API_KEY", "NOIR_SOVEREIGN_KEY_V72")
DEVICE_ID   = "NOIR_PC_CORE"

def register():
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        requests.post(f"{GATEWAY_URL}/agent/register", headers=headers, json={
            "device_id": DEVICE_ID,
            "agent": "Noir PC Agent (Windows)"
        }, timeout=10)
        print("[PC_AGENT] Registered successfully.")
    except Exception as e:
        print(f"[PC_AGENT] Registration failed: {e}")

def execute_cmd(cmd_data):
    cmd_id = cmd_data.get("command_id")
    action = cmd_data.get("action", {})
    atype  = action.get("type", action.get("action"))
    params = action.get("params", action)
    
    print(f"\n[PC_AGENT] Executing: {atype}")
    result = {"success": False, "output": ""}
    
    try:
        if atype == "shell" or atype == "cmd":
            command = params.get("cmd", "")
            out = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            result = {"success": True, "output": out.strip()}
            
        elif atype == "adb":
            # For USB debugging control of the phone FROM the PC
            adb_cmd = f"adb {params.get('cmd')}"
            out = subprocess.check_output(adb_cmd, shell=True, stderr=subprocess.STDOUT, text=True)
            result = {"success": True, "output": out.strip()}
            
        else:
            result = {"success": False, "error": "Unknown command for PC"}
            
    except Exception as e:
        result = {"success": False, "error": str(e)}
        
    print(f"Result: {result}")
    
    # Report back
    try:
        requests.post(f"{GATEWAY_URL}/agent/result", headers={"Authorization": f"Bearer {API_KEY}"}, json={
            "command_id": cmd_id,
            "device_id": DEVICE_ID,
            **result
        }, timeout=10)
    except Exception as e:
        print(f"[PC_AGENT] Failed to report result: {e}")

def run():
    print("🚀 Starting NOIR PC AGENT...")
    register()
    while True:
        try:
            resp = requests.get(f"{GATEWAY_URL}/agent/poll", params={"device_id": DEVICE_ID}, 
                              headers={"Authorization": f"Bearer {API_KEY}"}, timeout=15)
            if resp.status_code == 200:
                commands = resp.json().get("commands", [])
                for cmd in commands:
                    execute_cmd(cmd)
        except Exception as e:
            print(f"[PC_AGENT] Polling error: {e}")
            
        time.sleep(3)

if __name__ == "__main__":
    run()
