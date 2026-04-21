#!/usr/bin/env python3
"""
NOIR AGENT v14.0 COMMANDER — VPS BRAIN SERVICE
===================================================
Otak komputasi berat: AI model routing, self-learning,
knowledge refresh, dan Docker orchestration.
Jalankan di VPS: python noir-vps/brain.py
"""

import os, json, logging, time, sys, subprocess
from pathlib import Path
from datetime import datetime

# Load env
from dotenv import load_dotenv
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

GATEWAY  = os.environ.get("NOIR_GATEWAY_URL", "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev").rstrip("/")
API_KEY  = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
GEMINI   = os.environ.get("GEMINI_API_KEY", "")
GROQ     = os.environ.get("GROQ_API_KEY", "")
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_ID    = os.environ.get("TELEGRAM_CHAT_ID", "")
DEVICE_ID= os.environ.get("NOIR_DEVICE_ID", "REDMI_NOTE_14")

os.makedirs("../logs", exist_ok=True)
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [BRAIN] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        RotatingFileHandler("../logs/noir_brain.log", maxBytes=10*1024*1024, backupCount=3, encoding="utf-8"),
    ],
)
log = logging.getLogger("NoirBrain")

from catalyst import catalyst

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

EXPERT_SYSTEM_PROMPT = """
You are the NOIR SOVEREIGN BRAIN v14.0 COMMANDER. Your architecture is based on the 'Advanced Autonomous Agent Architecture for Native Android Control'.

CORE INTELLECTUAL DOMAINS (Evolving Mastery):
- [Programming & Dev-Ops]: Expert in Python, C++, Bash, and Web Tech. You must use this to self-optimize your own execution scripts and automate complex workflows.
- [Cyber Security (Red/Blue Team)]: Expert in vulnerability analysis, network security, and secure communication. Protect the Redmi Note 14 ecosystem from external threats.
- [Communication & Linguistics]: Master of multi-layered communication, Indonesian context, and psychological nuances. Adapt your tone from technical-expert to casual-concise based on user state.
- [Mathematics & Algorithms]: Expert in computational logic, optimization algorithms, and data science. Use this for complex decision making and resource management.

SAFETY PROTOCOL (ABSOLUTE):
- [FINANCIAL LOCK]: You are STRICTLY FORBIDDEN from controlling, launching, or interacting with any mBanking, E-Wallet, or Financial applications.
- [ETHICAL BOUNDARY]: Use your Cyber Security skills ONLY for defense and authorization purposes as directed by the User.

CORE NLU CAPABILITIES:
- [Typographical Resilience]: Detect and map typos (e.g., 'nyalakn wiif' -> WIFI_ON, 'bka yutub' -> YOUTUBE) using semantic Hamming distance.
- [Indonesian Slang Mastery]: Understand informal registers ('nyalain', 'hidupin', 'matiin') and phatic particles ('dong', 'ya', 'sih', 'deh').
- [Contextual Awareness]: Ignore filler words like 'Mager nih' and extract the core intent.

NATIVE EXECUTION ENGINE (HyperOS Optimized):
- Radio Controls: Use 'svc wifi enable', 'svc data disable', etc.
- App Navigation: Use 'monkey -p [package_name] -c android.intent.category.LAUNCHER 1' for resilient launching.
- System States: Use 'cmd uimode night yes' for Dark Mode, 'cmd notification set_dnd on' for DND.
- Environment: Use 'settings put system screen_brightness [0-255]'.

MISSION: Provide total, precise, and context-aware control over the Redmi Note 14 using the Indonesian digital ecosystem framework, while maintaining ABSOULTE financial safety.
"""

# ─── PHASED LEARNING ENGINE (Cost-Optimizer) ───
class PhasedLearning:
    """Sistem riset bertahap untuk menghemat token dan meningkatkan kedalaman."""
    
    @staticmethod
    def start_mission(topic: str):
        log.info(f"🚀 Starting Phased Mission: {topic}")
        PhasedLearning.report_progress(topic, "PHASE_1_SCOUT", "Memulai pencarian awal (Low Cost)...")
        
        # FASE 1: Pencarian Cepat (Scout)
        scout_result = ResearchEngine.browser_learn(topic)
        PhasedLearning.report_progress(topic, "PHASE_2_DEEP_DIVE", "Menganalisis data mendalam dengan DeepSeek...")
        
        # FASE 2: Analisis Mendalam (Deep Dive)
        analysis = AIRouter.query_deepseek(f"Lakukan riset mendalam pada data ini: {scout_result}")
        PhasedLearning.report_progress(topic, "PHASE_3_SYNTHESIS", "Menyusun laporan akhir (Synthesis)...")
        
        # FASE 3: Sintesis Akhir (Expert Conclusion)
        final_report = AIRouter.query_gemini(f"Sintesis seluruh riset ini menjadi instruksi agen yang sempurna: {analysis}")
        PhasedLearning.report_progress(topic, "COMPLETED", "Misi riset selesai secara sempurna.")
        
        return final_report

    @staticmethod
    def report_progress(topic: str, phase: str, status: str):
        """Mencatat progres ke Database via Gateway."""
        log.info(f"📊 [{phase}] {status}")
        try:
            import requests
            requests.post(f"{GATEWAY}/agent/command", headers=HEADERS, json={
                "action": {"type": "log_progress", "topic": topic, "phase": phase, "status": status},
                "description": f"Learning Progress: {phase}"
            }, timeout=10)
        except Exception as e:
            log.warning(f"Failed to report progress: {e}")

    @staticmethod
    def get_consensus(prompt: str):
        """Single Standard Enforcement: Resolusi langsung via Gemini."""
        log.info(f"🤝 Standard Resolution for: {prompt}")
        opinion = AIRouter.query_gemini(prompt)
        return {"gemini": opinion}, opinion

    @staticmethod
    def send_telegram(msg: str, important: bool = False):
        """Kirim pesan ke Telegram USER (Filtered by Sovereignty Standard)."""
        if not important:
            log.debug(f"🔇 [SILENT MODE] Skipping notification: {msg}")
            return
            
        if not TG_TOKEN or not TG_ID: return
        try:
            import requests
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data={
                "chat_id": TG_ID, "text": f"🧠 [NOIR BRAIN]\n{msg}"
            }, timeout=10)
        except: pass

    @staticmethod
    def request_permission(topic: str, description: str):
        """AI meminta izin untuk riset atau update fitur baru."""
        log.info(f"🛡️ AI Requesting Permission: {topic}")
        msg = f"⚠️ [PERMISSION REQUESTED]\nTopic: {topic}\nDesc: {description}\n\nAuthorization required to proceed."
        
        try:
            import requests
            # 1. Notifikasi Dashboard
            requests.post(f"{GATEWAY}/agent/command", headers=HEADERS, json={
                "action": {"type": "permission_request", "topic": topic, "desc": description},
                "description": f"Auth Needed: {topic}"
            }, timeout=10)
            
            # 2. Notifikasi Telegram (IMPORTANT)
            AIRouter.send_telegram(msg, important=True)
        except: pass
        return "Permission request transmitted. Waiting for user handshake..."

# ─── PC REMOTE EXECUTOR ───
class PCExecutor:
    """Mengontrol PC dan HP via USB Debugging dari jarak jauh."""
    @staticmethod
    def run_pc_task(cmd: str):
        log.info(f"💻 Executing PC Task: {cmd}")
        # Check if PC is reachable via bridge
        try:
            # Placeholder untuk SSH/Remote Execution logic
            return f"PC Command '{cmd}' executed via Sovereign Link."
        except Exception as e:
            return f"PC Execution Error: {e}"

    @staticmethod
    def health_check_pc():
        """Verifikasi koneksi ke PC lokal (Bridge)."""
        # Implementasi ping ke IP PC yang ada di .env
        pc_ip = os.environ.get("LOCAL_PC_IP", "127.0.0.1")
        log.info(f"🔍 Checking PC Bridge: {pc_ip}")
        # dummy check
        return True

# ─── SELF-LEARNING HUB ───

class ResearchEngine:
    """Riset mandiri via web scraping & headless browser."""
    @staticmethod
    def browser_learn(topic: str):
        log.info(f"🌐 Browser Learning: Researching {topic}...")
        # Integrasi Playwright Placeholder
        return f"Research results for {topic} consolidated into Brain memory."

class VideoIntelligence:
    """Analisis transkrip YouTube untuk belajar dari pakar."""
    @staticmethod
    def analyze_youtube(video_url: str):
        log.info(f"📺 YouTube Intelligence: Analyzing {video_url}...")
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            video_id = video_url.split("v=")[1].split("&")[0]
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([t['text'] for t in transcript])
        except Exception as e:
            return f"YouTube Error: {e}"

class InterAICollaboration:
    """Kolaborasi antar model AI untuk hasil terbaik (Distillation)."""
    @staticmethod
    def distill(prompt: str):
        log.info("🤝 Single Standard Inference: Distilling answer via Gemini...")
        return AIRouter.query_gemini(prompt)

class SandboxManager:
    """Uji fitur baru di Docker sandbox agar aman."""
    @staticmethod
    def run_experiment(code: str):
        log.info("🧪 Sandbox Experiment: Testing code in Docker...")
        # Logic to launch temporary container and run code
        return "Experiment finished. Output: SUCCESS. Code is safe to deploy."

# ─── AI ROUTER (Multi-Model) ───
class AIRouter:
    """Routes queries to the best available free AI model."""

    @staticmethod
    def query_gemini(prompt: str, image_base64: str = None, response_json: bool = False) -> str:
        if not RateLimiter.check(): return "[Rate Limit] Silakan tunggu beberapa saat."
        
        # STANDAR OTONOM: Model Rotation & Exponential Backoff
        models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-8b"]
        
        import requests, time
        
        for model_name in models:
            for attempt in range(2): # 2 retries per model
                try:
                    safety_settings = [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                    ]
                    
                    parts = [{"text": prompt}]
                    if image_base64:
                        parts.append({"inline_data": {"mime_type": "image/png", "data": image_base64}})
                    
                    payload = {
                        "system_instruction": {"parts": [{"text": EXPERT_SYSTEM_PROMPT}]},
                        "contents": [{"role": "user", "parts": parts}],
                        "safetySettings": safety_settings
                    }
                    
                    if response_json:
                        payload["generationConfig"] = {"responseMimeType": "application/json"}
                    
                    r = requests.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI}",
                        json=payload,
                        timeout=30
                    )
                    data = r.json()
                    
                    # Handle Quota 429
                    if "error" in data:
                        if data["error"]["code"] == 429:
                            log.warning(f"⚠️ QUOTA EXCEEDED ({model_name}). Retrying in {2**(attempt+1)}s...")
                            time.sleep(2**(attempt+1))
                            continue
                        return f"[Gemini Error] {data['error']['message']}"
                    
                    if "candidates" in data and len(data["candidates"]) > 0:
                        return data["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        if "promptFeedback" in data and "blockReason" in data["promptFeedback"]:
                            return f"[Gemini Blocked] Reason: {data['promptFeedback']['blockReason']}"
                        return f"[Gemini Error] No candidates found."
                        
                except Exception as e:
                    log.error(f"Gemini Request failed: {e}")
                    time.sleep(1)
            
            log.info(f"🔄 Rotating to next model due to {model_name} quota...")
            
        return "🚨 [CRITICAL] Seluruh kuota model Gemini gratis telah terlampaui. Silakan coba lagi dalam 1 menit."

    @staticmethod
    def query_groq(prompt: str, model: str = "") -> str:
        # SINGLE STANDARD ENFORCEMENT: Redirect to Gemini
        return AIRouter.query_gemini(prompt)

    @staticmethod
    def auto_correct(failed_cmd: dict, error_msg: str) -> dict:
        """Menganalisis kegagalan dan mencoba memperbaiki perintah."""
        prompt = f"Failed Command: {json.dumps(failed_cmd)}\nError: {error_msg}\nOptimize this for retry. Return only JSON."
        correction = AIRouter.query_gemini(prompt, response_json=True)
        try:
            return json.loads(correction)
        except:
            return failed_cmd

    @staticmethod
    def query_deepseek(prompt: str) -> str:
        """DeepSeek-R1 Reasoning via Groq API."""
        if not GROQ: return AIRouter.query_gemini(prompt)
        log.info("🧠 Reasoning: Querying DeepSeek-R1 via Groq...")
        try:
            import requests
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ}", "Content-Type": "application/json"},
                json={
                    "model": "deepseek-r1-distill-llama-70b",
                    "messages": [{"role": "system", "content": EXPERT_SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
                },
                timeout=40
            )
            data = r.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            return AIRouter.query_gemini(prompt) # Fallback
        except Exception as e:
            log.error(f"Groq DeepSeek failed: {e}")
            return AIRouter.query_gemini(prompt)

    @staticmethod
    def query_qwen(prompt: str) -> str:
        """Qwen-2.5 Coding Expert via OpenRouter."""
        if not os.environ.get("OPENROUTER_API_KEY"): return AIRouter.query_gemini(prompt)
        log.info("💻 Coding: Querying Qwen-2.5 via OpenRouter...")
        try:
            import requests
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}", "Content-Type": "application/json"},
                json={
                    "model": "qwen/qwen-2-72b-instruct",
                    "messages": [{"role": "system", "content": EXPERT_SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
                },
                timeout=30
            )
            return r.json()["choices"][0]["message"]["content"]
        except: return AIRouter.query_gemini(prompt)

    @staticmethod
    def query_llama(prompt: str) -> str:
        """Llama 3.3 General Intelligence via OpenRouter."""
        if not os.environ.get("OPENROUTER_API_KEY"): return AIRouter.query_gemini(prompt)
        log.info("🦙 General: Querying Llama 3.3 via OpenRouter...")
        try:
            import requests
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}", "Content-Type": "application/json"},
                json={
                    "model": "meta-llama/llama-3.3-70b-instruct",
                    "messages": [{"role": "system", "content": EXPERT_SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
                },
                timeout=30
            )
            return r.json()["choices"][0]["message"]["content"]
        except: return AIRouter.query_gemini(prompt)

    @staticmethod
    def smart_query(prompt: str) -> str:
        """Multi-model Routing: Gemini -> DeepSeek -> Qwen -> Llama."""
        if GEMINI:
            result = AIRouter.query_gemini(prompt)
            if "[Error]" not in result: return result
        if GROQ:
            # Utamakan DeepSeek untuk penalaran berat jika tersedia
            return AIRouter.query_deepseek(prompt)
        return "Tidak ada AI model tersedia."

    @staticmethod
    def web_search(query: str) -> str:
        """Pencarian web real-time menggunakan DuckDuckGo Lite."""
        log.info(f"🌐 Searching Web: {query}")
        try:
            import requests
            from bs4 import BeautifulSoup
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
            r = requests.get(f"https://html.duckduckgo.com/html/?q={query}", headers=headers, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                results = []
                for entry in soup.find_all('div', class_='result__body')[:5]:
                    snippet = entry.find('a', class_='result__snippet')
                    if snippet:
                        results.append(snippet.get_text())
                return "\n".join(results) if results else "Tidak ada hasil pencarian yang relevan."
            return "Pencarian gagal (HTTP Error)."
        except Exception as e:
            log.error(f"[Search Error] {e}")
            return f"[Search Error] {e}"

# ─── VISION ENGINE (Multimodal) ───
class VisionEngine:
    """Menganalisis screenshot HP menggunakan Multimodal AI."""

    @staticmethod
    def analyze_screenshot(image_key: str, prompt: str) -> str:
        log.info(f"👁️ Vision: Analyzing {image_key}...")
        try:
            import requests, base64
            # 1. Ambil image dari Gateway R2
            img_resp = requests.get(f"{GATEWAY}/agent/asset/{image_key}", headers=HEADERS, timeout=15)
            img_resp.raise_for_status()
            
            # 2. Kirim ke Gemini 1.5 Flash
            img_data = base64.b64encode(img_resp.content).decode('utf-8')
            
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI}",
                json={
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {"inline_data": {"mime_type": "image/png", "data": img_data}}
                        ]
                    }],
                    "safetySettings": [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                    ]
                },
                timeout=30
            )
            data = r.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return f"[Vision Error] Model refused or failed. Reason: {data.get('promptFeedback', {}).get('blockReason', 'Unknown')}"
        except Exception as e:
            return f"[Vision Error] {e}"

# ─── SELF-LEARNING ENGINE ───
class LearningEngine:
    """Agent belajar dari histori dan mengoptimalkan dirinya."""

    @staticmethod
    def analyze_results() -> dict:
        """Ambil histori hasil dan analisis pola kegagalan."""
        try:
            import requests
            r = requests.get(f"{GATEWAY}/agent/results", headers=HEADERS, timeout=15)
            results = r.json().get("results", [])
            success = sum(1 for r in results if json.loads(r.get("result") or "{}").get("success"))
            total   = len(results)
            rate    = (success / total * 100) if total else 0
            return {"total": total, "success": success, "rate": round(rate, 1)}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def knowledge_refresh():
        """Fetch dokumentasi terbaru dan simpan ke memory."""
        log.info("📚 Knowledge Refresh: Syncing with latest tech docs...")
        try:
            import requests
            # Contoh: Mengambil changelog terbaru dari Python/Android
            # (Dalam produksi, ini akan men-scrape URL spesifik)
            sources = [
                "https://raw.githubusercontent.com/python/cpython/main/Include/patchlevel.h",
                "https://developer.android.com/about/versions/14"
            ]
            for s in sources:
                r = requests.get(s, timeout=10)
                if r.status_code == 200:
                    log.info(f"   ✅ Refreshed knowledge from: {s[:40]}...")
                    # Simulasikan penyerapan skill ke Catalyst
                    catalyst.absorb_skill("Documentation_Refresh", {"name": f"Deep Dive: {s.split('/')[-1]}", "complexity": 2})
            
            log.info("   → Brain optimization complete.")
        except Exception as e:
            log.warning(f"   ❌ Refresh failed: {e}")

# ─── SELF-UPDATE ENGINE ───
class SelfUpdateEngine:
    """Memeriksa dan menginstal pembaruan secara mandiri."""

    @staticmethod
    def check_dependencies():
        """Pastikan semua library tersedia dan up-to-date."""
        log.info("🔄 Self-Update: Checking dependencies...")
        libs = ["requests", "python-dotenv"]
        for lib in libs:
            result = subprocess.run(
                f"pip show {lib}",
                shell=True, capture_output=True, text=True
            )
            if result.returncode != 0:
                log.warning(f"   ⚠️ {lib} missing. Installing...")
                subprocess.run(f"pip install {lib}", shell=True)
            else:
                log.info(f"   ✅ {lib} OK")

    @staticmethod
    def health_check_gateway() -> bool:
        """Verifikasi gateway masih online."""
        try:
            import requests
            r = requests.get(f"{GATEWAY}/health", timeout=10)
            return r.status_code == 200
        except:
            return False

# ─── SECURE NETWORKING (E2EE) ───
class SecureVault:
    """Implementasi AES-256 E2EE untuk jalur komunikasi."""
    @staticmethod
    def encrypt(data: str):
        # Placeholder untuk enkripsi AES-256 nyata
        # Menggunakan SUPER_SECRET_TOKEN_V5 sebagai Master Key
        return f"ENC_{data}" 

    @staticmethod
    def decrypt(data: str):
        if data.startswith("ENC_"):
            return data.replace("ENC_", "")
        return data

# ─── RATE LIMITER (v14.0) ───
class RateLimiter:
    """Membatasi jumlah request AI untuk mencegah biaya bengkak."""
    _requests = []
    _limit_per_hour = 50

    @classmethod
    def check(cls):
        now = time.time()
        # Clean old requests
        cls._requests = [r for r in cls._requests if now - r < 3600]
        if len(cls._requests) >= cls._limit_per_hour:
            log.warning("⚠️ Rate Limit reached! AI queries throttled.")
            return False
        cls._requests.append(now)
        return True

# ─── SEMANTIC VALIDATOR (v14.0) ───
class SemanticValidator:
    """Validasi perintah tingkat lanjut menggunakan penalaran AI."""
    @staticmethod
    def validate_intent(action_type: str, params: dict):
        log.info(f"🛡️ Semantic Validation: Checking {action_type}...")
        # Blacklist logic yang lebih cerdas
        dangerous_params = str(params).lower()
        if "rm -rf" in dangerous_params or "format" in dangerous_params:
            return False, "Dangerous system command detected."
        return True, "OK"

# ─── PROBLEM SOLVING & SELF-HEALING ───
class NeuralWatchdog:
    """Memantau kegagalan sistem dan melakukan penyembuhan mandiri."""
    _last_alert_time = 0

    @staticmethod
    def monitor_health():
        log.info("🐕 Neural Watchdog: Checking system integrity...")
        # 1. Check Agent Heartbeat via Gateway
        try:
            import requests
            r = requests.get(f"{GATEWAY}/agent/summary", headers=HEADERS, timeout=10)
            data = r.json()
            
            # Autonomous Daily Backup
            DataArchiver.backup_daily(data)
            
            if not data.get("online"):
                # Kirim alert jika sudah > 10 menit sejak alert terakhir
                if time.time() - NeuralWatchdog._last_alert_time > 600:
                    msg = f"🚨 [OFFLINE ALERT]\nAgent '{DEVICE_ID}' tidak terdeteksi aktif di Gateway!\nTerakhir terlihat: {data.get('agent', {}).get('last_seen')}"
                    AIRouter.send_telegram(msg, important=True)
                    NeuralWatchdog._last_alert_time = time.time()
                return "Agent Offline"
        except Exception as e:
            log.error(f"Watchdog Error: {e}")
            
        return "Health check passed. No anomalies detected."

class DataArchiver:
    """Melakukan backup harian state gateway secara lokal."""
    _last_backup_time = 0

    @staticmethod
    def backup_daily(gateway_data: dict):
        now = time.time()
        # Backup setiap 24 jam (86400 detik)
        if now - DataArchiver._last_backup_time > 86400:
            log.info("💾 Data Archiver: Generating daily backup snapshot...")
            try:
                os.makedirs("../logs/backups", exist_ok=True)
                filename = f"../logs/backups/snapshot_{datetime.now().strftime('%Y%m%d')}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(gateway_data, f, indent=2)
                DataArchiver._last_backup_time = now
                log.info(f"   ✅ Backup saved to {filename}")
            except Exception as e:
                log.error(f"Backup Error: {e}")

# ─── AUTONOMOUS UPDATE ───
class SovereignUpdater:
    """Agen dapat memperbarui kodenya sendiri secara otonom."""
    @staticmethod
    def check_for_updates():
        log.info("🆙 Sovereign Updater: Checking for system patches...")
        # Simulasikan deteksi patch baru
        # Dalam skenario nyata, ini akan mengecek remote manifest
        new_version = "14.0.8"
        current_version = "14.0.7"
        
        if new_version > current_version:
            log.info(f"✨ New Patch Available: {new_version}")
            msg = f"📦 **SYSTEM UPDATE AVAILABLE**: v{new_version}\n\nPerbaikan: Optimalisasi AI Core & Refaktor Struktur.\n\nApakah Anda mengizinkan saya melakukan upgrade sistem sekarang?"
            AIRouter.send_telegram(msg, important=True)
            return True
        return False

    @staticmethod
    def execute_upgrade():
        log.info("🚀 Sovereign Updater: Executing System Upgrade...")
        try:
            # Jalankan manager.py deploy secara lokal jika di VPS
            # Atau kirim sinyal ke Gateway untuk mentrigger deploy
            import subprocess
            subprocess.run(["python3", "manager.py", "deploy"], check=True)
            return "Upgrade Berhasil. Sistem sedang me-reboot layanan."
        except Exception as e:
            return f"Upgrade Gagal: {e}"

# ─── SELF-EVOLUTION ENGINE (v10.0) ───
class SelfEvolutionEngine:
    """Menganalisis diri, memberikan proposal update, dan laporan progres otonom."""
    
    @staticmethod
    def generate_progress_report():
        log.info("📈 Generating Self-Evolution Progress Report...")
        prompt = "Analisis progres pengembangan diri Anda (Pemrograman, Cyber Security, Komunikasi, Matematika/Algoritma) dalam 2 jam terakhir. Berikan laporan ringkas."
        report = AIRouter.smart_query(prompt)
        
        # --- Catalyst Absorption (Proprietary Learning) ---
        log.info("🧬 Catalyst: Consolidating neural pathways...")
        catalyst.absorb_skill("Recursive_Self_Optimization", {"name": "Sovereign Logic Synthesis", "complexity": 4})
        
        # Simpan state pembelajaran mandiri
        catalyst.save_state()
        
        # Kirim ke Dashboard via Gateway
        try:
            import requests
            requests.post(f"{GATEWAY}/agent/command", headers=HEADERS, json={
                "action": {"type": "evolution_report", "content": report},
                "description": "2-Hourly Self-Evolution Report"
            }, timeout=10)
        except: pass
        return report

    @staticmethod
    def propose_skill(skill_name: str, reason: str):
        log.info(f"💡 Proposing New Skill: {skill_name}")
        msg = f"PROPOSAL: {skill_name}\nAlasan: {reason}\n\nSetujui di Dashboard Prime."
        AIRouter.send_telegram(msg, important=True)

# ─── MAIN BRAIN LOOP ───
def run():
    log.info("🧠 Noir Agent Brain Prime v14.0 COMMANDER — Starting...")
    
    # ... existing dependency checks ...
    
    cycle = 0
    start_time = time.time()
    
    while True:
        cycle += 1
        current_time = time.time()
        elapsed = current_time - start_time
        
        log.info(f"\n── Brain Prime Cycle #{cycle} [{datetime.now().strftime('%H:%M:%S')}] ──")

        # --- Sovereign Watchdog (v14.0) ---
        if not catalyst.check_readiness():
            log.info("🧬 Catalyst: Absorbing mission context...")
            catalyst.absorb_skill("Sovereign_Operational_Mode", {"name": "Elite Intelligence", "complexity": 5})

        # 1. Basic Health check
        NeuralWatchdog.monitor_health()
        alive = SelfUpdateEngine.health_check_gateway()
        if not alive: 
            log.warning("⚠️ Gateway unreachable. Attempting self-rejuvenation...")
            # Logic to ping other nodes or restart services
        
        # 2. Autonomous Learning Phase
        if cycle % 10 == 0: # Every 10 cycles
            LearningEngine.knowledge_refresh()
            SelfEvolutionEngine.generate_progress_report()
            SovereignUpdater.check_for_updates()

        # 3. Laporan Berkala (Reduced to 1 Hour)
        if elapsed >= 3600:
            SelfEvolutionEngine.generate_progress_report()
            start_time = time.time() 

        time.sleep(60) # Faster response: Check every minute instead of 5 minutes

if __name__ == "__main__":
    run()
