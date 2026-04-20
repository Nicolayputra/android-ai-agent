#!/usr/bin/env python3
"""
NOIR MASTER MANAGER v13.0 ELITE-SOVEREIGN
========================================
The unified orchestrator for Gateway, VPS, and Mobile App layers.
Authority: ABSOLUTE SOVEREIGN
"""

import os, sys, time, subprocess, json
from pathlib import Path

# Try to load paramiko for VPS deployment
try:
    import paramiko
    from scp import SCPClient
    HAS_SSH = True
except ImportError:
    HAS_SSH = False

def log(msg, level="INFO"):
    icons = {"INFO": ">>", "SUCCESS": "OK", "WARNING": "!!", "ERROR": "XX", "PROCESS": ".."}
    print(f"{icons.get(level, '--')} [NOIR MANAGER] {msg}")

def run_cmd(cmd, cwd=None):
    try:
        result = subprocess.run(cmd, shell=True, check=True, cwd=cwd, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        log(f"Command failed: {e.stderr}", "ERROR")
        return None

class NoirManager:
    def __init__(self):
        self.config = self.load_env()

    def load_env(self):
        env = {}
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        k, v = line.strip().split("=", 1)
                        env[k.strip()] = v.strip()
        return env

    def deploy_gateway(self):
        log("Initiating Gateway Deployment (Cloudflare)...", "PROCESS")
        res = run_cmd("npx wrangler deploy", cwd="noir-gateway")
        if res:
            log("Gateway Deployed Successfully.", "SUCCESS")
        else:
            log("Gateway Deployment Failed.", "ERROR")

    def deploy_vps(self):
        if not HAS_SSH:
            log("paramiko/scp not installed. Cannot deploy to VPS automatically.", "ERROR")
            log("Run: pip install paramiko scp", "INFO")
            return

        host = self.config.get("VPS_ALIBABA_IP", "8.215.23.17")
        user = "root"
        pw = "N!colay_No1r.Ai@Agent#Secure" # Hardcoded in old script, should be in .env

        log(f"Connecting to VPS {host}...", "PROCESS")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            log("Attempting SSH handshake...", "PROCESS")
            ssh.connect(host, username=user, password=pw, timeout=60)
            log("SSH Connection Established.", "SUCCESS")
            
            # Sync files
            log("Compressing local files...", "PROCESS")
            tar_file = "project.tar.gz"
            # Explicitly use tar if available or ignore if already exists
            run_cmd(f"tar -czf {tar_file} --exclude='node_modules' --exclude='venv' --exclude='.git' --exclude='mobile_app/.buildozer' .")
            
            log(f"Uploading {tar_file} to VPS...", "PROCESS")
            with SCPClient(ssh.get_transport()) as scp:
                scp.put(tar_file, f"/root/{tar_file}")
            log("Upload completed.", "SUCCESS")
                
            log("Activating Brain on VPS...", "PROCESS")
            cmds = [
                "mkdir -p /root/noir-agent",
                f"tar -xzf /root/{tar_file} -C /root/noir-agent",
                "cd /root/noir-agent && docker-compose down",
                "cd /root/noir-agent && docker-compose up -d --build"
            ]
            for cmd in cmds:
                log(f"Executing: {cmd}", "PROCESS")
                stdin, stdout, stderr = ssh.exec_command(cmd)
                stdout.channel.recv_exit_status() # Wait for cmd
            
            log("VPS Infrastructure ACTIVE.", "SUCCESS")
        except Exception as e:
            log(f"VPS Deployment Error: {e}", "ERROR")
        finally:
            ssh.close()

    def build_apk(self):
        log("Checking APK Build Environment...", "PROCESS")
        res = run_cmd("buildozer --version")
        if res:
            log(f"Buildozer detected: {res}", "SUCCESS")
            log("Recommendation: Run 'buildozer android debug' manually for full build.", "INFO")
        else:
            log("Buildozer not found. Use GitHub Actions for APK generation.", "WARNING")

    def health_check(self):
        log("=== HEALTH AUDIT v13.0 ===", "INFO")
        # Check Gateway
        gw_url = self.config.get("NOIR_GATEWAY_URL", "")
        if gw_url:
            try:
                import requests
                r = requests.get(f"{gw_url}/health", timeout=5)
                log(f"Gateway Health: {r.status_code} ({r.json().get('status','?')})", "SUCCESS" if r.status_code==200 else "ERROR")
            except:
                log("Gateway Unreachable.", "ERROR")
        
        # Check VPS
        vps_ip = self.config.get("VPS_ALIBABA_IP", "")
        if vps_ip:
            res = run_cmd(f"ping -n 1 {vps_ip}" if sys.platform == "win32" else f"ping -c 1 {vps_ip}")
            log(f"VPS Ping: {'OK' if res else 'FAILED'}", "SUCCESS" if res else "ERROR")

    def show_menu(self):
        while True:
            print(f"\n{'='*20} NOIR MASTER MANAGER v13.0 {'='*20}")
            print("1. Full Deployment (Gateway + VPS)")
            print("2. Deploy Gateway Only")
            print("3. Deploy VPS Only")
            print("4. APK Build Status")
            print("5. Health Check (Audit)")
            print("0. Exit")
            print("="*67)
            
            choice = input("Select Option > ").strip()
            if choice == "1":
                self.deploy_gateway()
                self.deploy_vps()
            elif choice == "2":
                self.deploy_gateway()
            elif choice == "3":
                self.deploy_vps()
            elif choice == "4":
                self.build_apk()
            elif choice == "5":
                self.health_check()
            elif choice == "0":
                break
            else:
                print("Invalid selection.")

if __name__ == "__main__":
    manager = NoirManager()
    if len(sys.argv) > 1:
        # CLI Mode
        cmd = sys.argv[1]
        if cmd == "deploy": manager.deploy_vps()
        elif cmd == "gateway": manager.deploy_gateway()
        elif cmd == "check": manager.health_check()
    else:
        # Interactive Mode
        manager.show_menu()
