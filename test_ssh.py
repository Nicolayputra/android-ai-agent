import paramiko
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("8.215.23.17", username="root", password="N!colay_No1r.Ai@Agent#Secure", timeout=10)
    print("SUCCESS")
    ssh.close()
except Exception as e:
    print(f"FAILED: {e}")
