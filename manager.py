import os, sys, shutil, json, time, subprocess

class NoirManager:
    def __init__(self):
        # Fallback to hardcoded IP if not in env
        self.vps_ip = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
        self.vps_user = os.environ.get("NOIR_VPS_USER", "root")
        self.remote_path = "/root/noir-agent"
        self.ssh_base = ["ssh", f"{self.vps_user}@{self.vps_ip}"]

    def deploy_vps(self):
        print("[PROCESS] Syncing to VPS (v14.0 COMMANDER)...")
        try:
            # Sync files
            subprocess.run(["scp", "-r", ".", f"{self.vps_user}@{self.vps_ip}:{self.remote_path}"], check=True)
            # Kill existing standalone process and docker containers
            subprocess.run(self.ssh_base + ["fuser -k 80/tcp || true"])
            subprocess.run(self.ssh_base + [f"cd {self.remote_path} && docker-compose down || true"])
            
            # Start all services in Docker (Brain, Telegram, Dashboard)
            print("[PROCESS] Starting All Neural Services in Docker...")
            subprocess.run(self.ssh_base + [f"cd {self.remote_path} && docker-compose up -d --build"], check=True)
            
            print("[SUCCESS] v14.0 COMMANDER DEPLOYED.")
        except Exception as e:
            print(f"[ERROR] Deployment failed: {e}")

    def clean_vps(self):
        print("[PROCESS] Purging VPS Cache...")
        try:
            subprocess.run(self.ssh_base + ["docker system prune -af --volumes"], check=True)
            print("[SUCCESS] Cache Purged.")
        except Exception as e:
            print(f"[ERROR] Cleanup failed: {e}")

    def gateway_deploy(self):
        print("[PROCESS] Deploying Cloudflare Gateway...")
        try:
            subprocess.run(["npx", "wrangler", "deploy"], check=True, cwd="noir-gateway")
            print("[SUCCESS] Gateway LIVE.")
        except Exception as e:
            print(f"[ERROR] Gateway deploy failed: {e}")

    def health_check(self):
        print("[PROCESS] Running Diagnostics...")
        subprocess.run(self.ssh_base + ["docker ps"])
        subprocess.run(self.ssh_base + ["lsof -i :80"])

if __name__ == "__main__":
    manager = NoirManager()
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "deploy": manager.deploy_vps()
        elif cmd == "gateway": manager.gateway_deploy()
        elif cmd == "check": manager.health_check()
        elif cmd == "clean": manager.clean_vps()
    else:
        print("Usage: python manager.py [deploy|gateway|check|clean]")
