#!/usr/bin/env python3
"""
NOIR AGENT v7.5 — TELEGRAM SOVEREIGN INTERFACE
=============================================
Bot Telegram cerdas dengan integrasi AI Brain.
"""

import os, json, logging, sys, re
from pathlib import Path

# Load env
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

try:
    import requests
    from telebot import TeleBot, types
    # Import AIRouter from brain
    sys.path.append(os.path.dirname(__file__))
    from brain import AIRouter
except ImportError:
    print("Install: pip install pyTelegramBotAPI requests")
    sys.exit(1)

BOT_TOKEN  = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID    = os.environ.get("TELEGRAM_CHAT_ID", "")
GATEWAY    = os.environ.get("NOIR_GATEWAY_URL", "").rstrip("/")
API_KEY    = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")

if not BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN belum diisi di .env")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("NoirTelegramBot")

bot = TeleBot(BOT_TOKEN)
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

SYSTEM_PROMPT = """
You are the NOIR SOVEREIGN BRAIN. You control a Redmi Note 14 agent.
If the user wants an action, YOU MUST include one of these tags in your response:
- [ACTION:screenshot]
- [ACTION:battery]
- [ACTION:shell, cmd="command here"]
- [ACTION:info]

Example: "Sesuai perintah, saya akan mengambil screenshot sekarang. [ACTION:screenshot]"
Respond in Indonesian. Be professional, cold, and sovereign.
"""

def cloud_cmd(action_type: str, params: dict = None, desc: str = "") -> dict:
    try:
        r = requests.post(
            f"{GATEWAY}/agent/command",
            headers=HEADERS,
            json={"action": {"type": action_type, **(params or {})}, "description": desc or action_type},
            timeout=15
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def is_authorized(msg) -> bool:
    return not CHAT_ID or str(msg.chat.id) == CHAT_ID

def make_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📸 Screenshot", "🔋 Baterai")
    markup.row("ℹ️ Info Agent", "📋 Histori")
    markup.row("🖥️ Terminal", "🤖 Tanya AI")
    return markup

@bot.message_handler(commands=["start", "help"])
def cmd_start(msg):
    if not is_authorized(msg):
        bot.reply_to(msg, "⛔ Akses ditolak.")
        return
    bot.send_message(
        msg.chat.id,
        "🖤 *NOIR SOVEREIGN CORE v7.5*\n\nKewenangan Mutlak: USER\nSistem AI: Gemini 1.5 Flash Aktif.\n\nKirim perintah langsung atau tanya apa pun.",
        parse_mode="Markdown",
        reply_markup=make_menu()
    )

@bot.message_handler(func=lambda m: True)
def handle_all(msg):
    if not is_authorized(msg):
        bot.reply_to(msg, "⛔ Akses ditolak.")
        return

    text = msg.text.strip()
    bot.send_chat_action(msg.chat.id, "typing")

    # 1. Hardcoded Shortcuts (Fast Response)
    if text in ["📸 Screenshot", "screenshot"]:
        r = cloud_cmd("screenshot", desc="Telegram Shortcut")
        bot.reply_to(msg, f"📸 Perintah dikirim: `{r.get('command_id', 'QUEUED')}`", parse_mode="Markdown")
        return
    
    if text in ["🔋 Baterai", "battery"]:
        r = cloud_cmd("battery", desc="Telegram Shortcut")
        bot.reply_to(msg, f"🔋 Perintah dikirim: `{r.get('command_id', 'QUEUED')}`", parse_mode="Markdown")
        return

    # 2. AI Processing (Brain Integration)
    log.info(f"🧠 Querying Brain for: {text}")
    ai_resp = AIRouter.smart_query(f"{SYSTEM_PROMPT}\n\nUSER: {text}")
    
    # Check for Actions in AI Response
    actions_found = re.findall(r'\[ACTION:(.*?)\]', ai_resp)
    
    for action_str in actions_found:
        if "screenshot" in action_str: cloud_cmd("screenshot", desc=f"AI: {text}")
        elif "battery" in action_str: cloud_cmd("battery", desc=f"AI: {text}")
        elif "shell" in action_str:
            cmd_match = re.search(r'cmd="(.*?)"', action_str)
            if cmd_match: cloud_cmd("shell", {"cmd": cmd_match.group(1)}, desc=f"AI Shell: {text}")
        elif "info" in action_str: cloud_cmd("info", desc=f"AI: {text}")

    # Clean the response from tags
    clean_resp = re.sub(r'\[ACTION:.*?\]', '', ai_resp).strip()
    bot.reply_to(msg, clean_resp or "Perintah dipahami dan sedang dieksekusi.")

if __name__ == "__main__":
    log.info("🖤 Noir Sovereign Telegram Bot — Starting...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
