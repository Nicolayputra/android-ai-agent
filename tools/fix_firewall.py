import paramiko, sys, os
os.environ["PYTHONIOENCODING"] = "utf-8"

VPS_IP = "8.215.23.17"
VPS_USER = "root"
VPS_PASS = "N!colay_No1r.Ai@Agent#Secure"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=15)
    print("[OK] Connected to VPS")
except Exception as e:
    print(f"[FAIL] SSH failed: {e}")
    sys.exit(1)

commands = [
    # Check if server is running
    "ps aux | grep server.py | grep -v grep",
    # Check what's listening on 8765
    "ss -tlnp | grep 8765",
    # Open firewall port 8765
    "ufw allow 8765/tcp 2>/dev/null || true",
    "iptables -I INPUT -p tcp --dport 8765 -j ACCEPT 2>/dev/null || true",
    "iptables -I INPUT -p tcp --dport 8765 -j ACCEPT",
    # Also try firewalld
    "firewall-cmd --permanent --add-port=8765/tcp 2>/dev/null; firewall-cmd --reload 2>/dev/null || true",
    # Verify server responds locally
    "curl -s -o /dev/null -w 'HTTP %{http_code}' http://localhost:8765/",
    # Check if server log has errors
    "tail -5 /var/log/noir-dashboard.log",
]

for cmd in commands:
    print(f"\n> {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(f"  {out}")
    if err:
        print(f"  [stderr] {err}")

ssh.close()
print("\n[DONE] Firewall rules applied.")
