#!/usr/bin/env python3
"""
NOIR AGENT v6 — TELEGRAM INTERFACE
=====================================
Bot Telegram sebagai command interface untuk Noir Agent.
Jalankan di VPS atau PC: python noir-vps/telegram_bot.py
"""

import os, json, logging, sys
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
except ImportError:
    print("Install: pip install pyTelegramBotAPI requests")
    sys.exit(1)

BOT_TOKEN  = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID    = os.environ.get("TELEGRAM_CHAT_ID", "")
GATEWAY    = os.environ.get("NOIR_GATEWAY_URL", "").rstrip("/")
API_KEY    = os.environ.get("NOIR_API_KEY", "")

if not BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN belum diisi di .env")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("NoirTelegramBot")

bot = TeleBot(BOT_TOKEN)
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

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
    return str(msg.chat.id) == CHAT_ID

def make_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📸 Screenshot", "🔋 Baterai")
    markup.row("ℹ️ Info Agent", "📋 Histori")
    markup.row("🖥️ Shell Custom")
    return markup

@bot.message_handler(commands=["start", "help"])
def cmd_start(msg):
    if not is_authorized(msg):
        bot.reply_to(msg, "⛔ Akses ditolak.")
        return
    bot.send_message(
        msg.chat.id,
        "🖤 *NOIR AGENT v6.0 — Online*\n\nKewenangan Mutlak: USER\nPilih perintah:",
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

    if "screenshot" in text.lower() or "📸" in text:
        r = cloud_cmd("screenshot", desc="Screenshot via Telegram")
        bot.reply_to(msg, f"✅ Terkirim: `{r.get('command_id', r)}`", parse_mode="Markdown")

    elif "baterai" in text.lower() or "🔋" in text:
        r = cloud_cmd("battery", desc="Cek Baterai via Telegram")
        bot.reply_to(msg, f"✅ Terkirim: `{r.get('command_id', r)}`", parse_mode="Markdown")

    elif "info" in text.lower() or "ℹ️" in text:
        r = cloud_cmd("info", desc="Info Agent via Telegram")
        bot.reply_to(msg, f"✅ Terkirim: `{r.get('command_id', r)}`", parse_mode="Markdown")

    elif "histori" in text.lower() or "📋" in text:
        try:
            r = requests.get(f"{GATEWAY}/agent/results", headers=HEADERS, timeout=15)
            results = r.json().get("results", [])[:5]
            if not results:
                bot.reply_to(msg, "_(belum ada histori)_", parse_mode="Markdown")
                return
            lines = ["📋 *Histori Terakhir:*"]
            for res in results:
                data = json.loads(res.get("result") or "{}")
                ok = "✅" if data.get("success") else "❌"
                out = (data.get("output") or data.get("error") or "-")[:80]
                lines.append(f"{ok} `{res.get('description','?')[:30]}`\n   → {out}")
            bot.reply_to(msg, "\n\n".join(lines), parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(msg, f"❌ Error: {e}")

    elif "shell" in text.lower() or "🖥️" in text:
        bot.reply_to(msg, "Kirim perintah shell:\n`shell <perintah>`\nContoh: `shell ls /sdcard`", parse_mode="Markdown")

    elif text.lower().startswith("shell "):
        cmd = text[6:].strip()
        r = cloud_cmd("shell", {"cmd": cmd}, desc=f"shell: {cmd}")
        bot.reply_to(msg, f"✅ Dikirim: `{r.get('command_id', r)}`", parse_mode="Markdown")

    else:
        bot.reply_to(msg, "Tidak dikenal. Ketik /start untuk menu.", reply_markup=make_menu())

log.info("🖤 Noir Agent Telegram Bot — Starting...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)
