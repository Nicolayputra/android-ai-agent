"""
NOIR OMNI-SOVEREIGN INTEGRATED SERVER v13.0 ELITE-SOVEREIGN
=========================================================
Unified Gateway + Dashboard + Asset Manager.
Ultra-stable direct bridge for Redmi Note 14.
"""

import os, json, time, sys, sqlite3, shutil
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Noir Sovereign v13.0 ELITE-SOVEREIGN")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DIRECTORY SETUP ---
# Use relative paths for better portability
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "noir_sovereign.db")
ASSET_DIR = os.path.join(BASE_DIR, "assets")
os.makedirs(ASSET_DIR, exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS commands 
                 (id TEXT PRIMARY KEY, action TEXT, description TEXT, status TEXT, result TEXT, updated_at DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS agents 
                 (device_id TEXT PRIMARY KEY, name TEXT, last_seen DATETIME, stats TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- AGENT ENDPOINTS (Direct Bridge) ---

@app.post("/agent/register")
async def agent_register(request: Request):
    try:
        data = await request.json()
    except:
        return {"status": "error", "message": "Invalid JSON"}
        
    device_id = data.get("device_id")
    name = data.get("agent", "Unknown Agent")
    stats = json.dumps(data.get("stats", {}))
    
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO agents (device_id, name, last_seen, stats) VALUES (?, ?, CURRENT_TIMESTAMP, ?)", 
              (device_id, name, stats))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/agent/poll")
async def agent_poll(device_id: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, action FROM commands WHERE status = 'pending' LIMIT 5")
    rows = c.fetchall()
    cmds = []
    for row in rows:
        cmds.append({"command_id": row[0], "action": json.loads(row[1])})
        c.execute("UPDATE commands SET status = 'sent' WHERE id = ?", (row[0],))
    conn.commit()
    conn.close()
    return {"commands": cmds}

@app.post("/agent/result")
async def agent_result(request: Request):
    try:
        data = await request.json()
    except:
        return {"status": "error", "message": "Invalid JSON"}
        
    cid = data.get("command_id")
    res = json.dumps(data)
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE commands SET status = 'done', result = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (res, cid))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.post("/agent/upload")
async def agent_upload(file: UploadFile = File(...), device_id: str = "REDMI_NOTE_14"):
    key = f"ss_{int(time.time())}.png"
    file_path = os.path.join(ASSET_DIR, key)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"ok": True, "key": key}

@app.get("/agent/asset/{key}")
async def get_asset(key: str):
    file_path = os.path.join(ASSET_DIR, key)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Not found"}

# --- DASHBOARD API ---

@app.get("/api/status")
async def api_status():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT name, last_seen, stats FROM agents ORDER BY last_seen DESC LIMIT 1")
    agent = c.fetchone()
    is_online = False
    agent_data = None
    if agent:
        is_online = True 
        agent_data = {"name": agent["name"], "last_seen": agent["last_seen"], "stats": json.loads(agent["stats"]) if agent["stats"] else {}}
    c.execute("SELECT id, description, status, updated_at FROM commands ORDER BY updated_at DESC LIMIT 10")
    rows = c.fetchall()
    commands = [{"id": r["id"], "desc": r["description"], "status": r["status"], "ts": r["updated_at"]} for r in rows]
    conn.close()
    
    # Add Catalyst Status
    cat_data = {"growth_level": 0.1}
    if os.path.exists(os.path.join(BASE_DIR, "catalyst_knowledge.json")):
        with open(os.path.join(BASE_DIR, "catalyst_knowledge.json"), "r") as f:
            cat_data = json.load(f)

    return {"online": is_online, "agent": agent_data, "commands": commands, "catalyst": cat_data}

@app.post("/api/command")
async def api_command(request: Request):
    try:
        data = await request.json()
    except:
        return {"status": "error", "message": "Invalid JSON"}
        
    action = json.dumps(data.get("action", {}))
    desc = data.get("description", "Manual Control")
    cid = os.urandom(4).hex().upper()
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO commands (id, action, description, status, updated_at) VALUES (?, ?, ?, 'pending', CURRENT_TIMESTAMP)", 
              (cid, action, desc))
    conn.commit()
    conn.close()
    return {"status": "queued", "command_id": cid}

@app.get("/")
async def get_index():
    with open(os.path.join(BASE_DIR, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
