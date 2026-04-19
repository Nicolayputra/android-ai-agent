"""
NOIR OMNI-DASHBOARD v7
======================
High-Performance Web Dashboard for Sovereign AI Agent.
"""

import os, json, time, sys, asyncio, requests
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv

# Load ENV
load_dotenv()
GATEWAY = os.environ.get("NOIR_GATEWAY_URL", "").rstrip("/")
API_KEY = os.environ.get("NOIR_API_KEY", "")
DEVICE_ID = os.environ.get("NOIR_DEVICE_ID", "REDMI_NOTE_14")

app = FastAPI(title="Noir Omni-Dashboard v7")
BASE_DIR = Path(__file__).resolve().parent

# --- SERVICES ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.append(ws)
    def disconnect(self, ws: WebSocket):
        self.active_connections.remove(ws)
    async def broadcast(self, data: dict):
        for ws in self.active_connections:
            try: await ws.send_json(data)
            except: pass

manager = ConnectionManager()

# --- API ENDPOINTS ---
@app.get("/api/status")
async def get_status():
    try:
        r = requests.get(f"{GATEWAY}/health", timeout=5)
        return r.json()
    except:
        return {"error": "Gateway unreachable"}

@app.post("/api/command")
async def post_command(request: Request):
    data = await request.json()
    try:
        r = requests.post(f"{GATEWAY}/agent/command", 
                          headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                          json=data, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/neural")
async def neural_consensus(request: Request):
    data = await request.json()
    prompt = data.get("prompt")
    
    # Simulasi pemanggilan Konsensus dari Brain (VPS)
    # Ini akan memicu Gemini, DeepSeek, dan Qwen secara paralel
    opinions = {
        "gemini": f"Saran: Berdasarkan prompt '{prompt}', agen harus segera melakukan sinkronisasi data.",
        "deepseek": "Analisis: Struktur perintah ini aman untuk dieksekusi otonom pada HyperOS.",
        "qwen": "Rekomendasi: Tambahkan flag --force untuk memastikan shell command berjalan lancar."
    }
    return {"opinions": opinions, "status": "Consensus Active"}

@app.get("/")
async def get_index():
    with open(BASE_DIR / "index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
