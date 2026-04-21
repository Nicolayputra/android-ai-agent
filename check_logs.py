import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('8.215.23.17', username='root', password='N!colay_No1r.Ai@Agent#Secure')

# Check Brain Logs
_, stdout, stderr = ssh.exec_command('docker logs --tail 100 noir-brain')
with open('vps_brain_logs.txt', 'wb') as f:
    f.write(stdout.read())
    f.write(stderr.read())

# Check Dashboard Logs
_, stdout, stderr = ssh.exec_command('docker logs --tail 100 noir-dashboard')
with open('vps_dashboard_logs.txt', 'wb') as f:
    f.write(stdout.read())
    f.write(stderr.read())

# Check Telegram Logs
_, stdout, stderr = ssh.exec_command('docker logs --tail 100 noir-telegram')
with open('vps_telegram_logs.txt', 'wb') as f:
    f.write(stdout.read())
    f.write(stderr.read())

ssh.close()
