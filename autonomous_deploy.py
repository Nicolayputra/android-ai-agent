import paramiko

VPS_IP = "8.215.23.17"
VPS_USER = "root"
VPS_PASS = "N!colay_No1r.Ai@Agent#Secure"

print("[1] Connecting to VPS...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS)

print("[2] Uploading archive...")
sftp = ssh.open_sftp()
sftp.put("project.tar.gz", "/root/project.tar.gz")
sftp.close()

print("[3] Executing deployment...")
commands = [
    "mkdir -p /root/noir-agent",
    "tar -xzf /root/project.tar.gz -C /root/noir-agent",
    "rm /root/project.tar.gz",
    "fuser -k 80/tcp || true",
    "cd /root/noir-agent && docker-compose down || true",
    "cd /root/noir-agent && docker-compose up -d --build"
]

for cmd in commands:
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print(f"ERR: {err}")

ssh.close()
print("[SUCCESS] Fully Autonomous Deployment Completed!")
