import paramiko
from scp import SCPClient
import os, time

def deploy():
    host = "8.215.23.17"
    user = "root"
    pw = "N!colay_No1r.Ai@Agent#Secure"
    
    print(f"[NOIR] Attempting connection to VPS {host}...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=pw, timeout=30)
        print("OK: SSH Connection Successful.")
        
        # 1. Update & Install Docker
        print("Phase 1: Infrastructure Setup (Docker)")
        commands = [
            "export DEBIAN_FRONTEND=noninteractive",
            "apt-get update -y",
            "apt-get install -y docker.io docker-compose",
            "systemctl start docker",
            "systemctl enable docker"
        ]
        for cmd in commands:
            print(f"   Executing: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                print(f"   Warning: {cmd} returned code {exit_status}")
            
        # 2. Upload Files
        print("Phase 2: Project Synchronization")
        print("   Compressing local files...")
        tar_cmd = "tar -czf project.tar.gz --exclude='node_modules' --exclude='venv' --exclude='.git' --exclude='.buildozer' ."
        os.system(tar_cmd)
        
        print("   Uploading to VPS...")
        with SCPClient(ssh.get_transport()) as scp:
            scp.put("project.tar.gz", "/root/project.tar.gz")
            
        # 3. Extract & Run
        print("Phase 3: Brain Activation")
        setup_cmds = [
            "mkdir -p /root/noir-agent",
            "tar -xzf /root/project.tar.gz -C /root/noir-agent",
            "cd /root/noir-agent && docker-compose down", # Stop if running
            "cd /root/noir-agent && docker-compose up -d --build"
        ]
        for cmd in setup_cmds:
            print(f"   Executing: {cmd}")
            ssh.exec_command(cmd)
            time.sleep(2) # Small buffer
        
        print("\n[NOIR] MISSION ACCOMPLISHED!")
        print(f"Dashboard: http://{host}:8765")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()
