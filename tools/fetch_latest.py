import requests, sys, os
os.environ["PYTHONIOENCODING"] = "utf-8"

TOKEN = os.getenv("GITHUB_TOKEN", "YOUR_TOKEN_HERE")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github.v3+json"}

resp = requests.get("https://api.github.com/repos/Nicolayputra/android-ai-agent/actions/runs?per_page=1", headers=HEADERS).json()
run = resp["workflow_runs"][0]
print(f"Run #{run['run_number']} | ID: {run['id']} | Status: {run['status']} | Conclusion: {run['conclusion']}")

if run["status"] != "completed":
    print("Still running...")
    sys.exit(0)

jobs = requests.get(run["jobs_url"], headers=HEADERS).json()
for job in jobs.get("jobs", []):
    if job["conclusion"] == "failure":
        log = requests.get(f"https://api.github.com/repos/Nicolayputra/android-ai-agent/actions/jobs/{job['id']}/logs", headers=HEADERS).text
        lines = log.split('\n')
        
        # Save full log
        with open("full_log.txt", "w", encoding="utf-8") as f:
            f.write(log)
        
        # Find the REAL error - look for buildozer/command failed/toolchain errors
        keywords = ["command failed", "error:", "exception", "aidl", "not found", "unrecognized", "invalid", "buildozer failed"]
        for i, line in enumerate(lines):
            low = line.lower()
            if any(k in low for k in keywords):
                start = max(0, i - 3)
                end = min(len(lines), i + 3)
                context = '\n'.join(lines[start:end])
                try:
                    print(f"\n=== LINE {i} ===")
                    print(context.encode('ascii', 'replace').decode('ascii'))
                except:
                    pass
