#!/usr/bin/env python3
"""
NOIR AGENT v14.0 COMMANDER — TELEGRAM SOVEREIGN INTERFACE
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
    from brain import AIRouter
    from skill_acquisition import SkillAcquisitionEngine
    from linguistic_learning import LinguisticMastery
    from nlu_processor import NLUProcessor
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

from logging.handlers import RotatingFileHandler
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        RotatingFileHandler("../logs/noir_telegram.log", maxBytes=5*1024*1024, backupCount=2, encoding="utf-8")
    ]
)
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
        "🖤 *NOIR SOVEREIGN CORE v14.0*\n\n"
        "Kewenangan Mutlak: USER\n"
        "Sistem AI: COMMANDER\n\n"
        "🛠️ **Commands**:\n"
        "/learn [topik] - Ajarkan AI skill baru\n"
        "/skills - Lihat daftar skill otonom\n"
        "/start - Menu utama",
        parse_mode="Markdown",
        reply_markup=make_menu()
    )

@bot.message_handler(commands=["learn"])
def cmd_learn(msg):
    if not is_authorized(msg): return
    topic = msg.text.replace("/learn", "").strip()
    if not topic:
        bot.reply_to(msg, "💡 Gunakan: `/learn [topik]` (misal: `/learn image generator`)", parse_mode="Markdown")
        return
    
    bot.reply_to(msg, f"🧪 **EVOLUTION STARTED**: Mencari instrumen AI untuk `{topic}`...", parse_mode="Markdown")
    tool = SkillAcquisitionEngine.discover_and_integrate(topic)
    
    if "error" in tool:
        bot.reply_to(msg, f"❌ Gagal mengintegrasikan skill: {tool['error']}")
    else:
        bot.reply_to(msg, f"✅ **SKILL INTEGRATED**: `{tool['name']}`\n\n_{tool['description']}_", parse_mode="Markdown")

@bot.message_handler(commands=["skills"])
def cmd_skills(msg):
    if not is_authorized(msg): return
    skills = SkillAcquisitionEngine.get_integrated_skills()
    if not skills:
        bot.reply_to(msg, "📭 Belum ada skill otonom yang dipelajari.")
        return
    
    list_str = "🎓 **AUTONOMOUS SKILLS**:\n\n"
    for name, data in skills.items():
        list_str += f"- **{name}**: {data['description']}\n"
    
    bot.reply_to(msg, list_str, parse_mode="Markdown")

@bot.message_handler(commands=["absorb_language"])
def cmd_absorb(msg):
    if not is_authorized(msg): return
    bot.reply_to(msg, "🧠 **LINGUISTIC MISSION**: Menghubungkan ke ChatGPT interface untuk mempelajari pola bahasa manusia...")
    patterns = LinguisticMastery.absorb_human_patterns()
    
    if "error" in patterns:
        bot.reply_to(msg, f"❌ Gagal menyerap pola: {patterns['error']}")
    else:
        bot.reply_to(msg, f"✅ **ABSORPTION COMPLETE**: {len(patterns)} pola bahasa manusia telah diserap ke dalam memori kognitif Noir.", parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_photo(msg):
    if not is_authorized(msg): return
    bot.reply_to(msg, "👁️ **VISION INTELLIGENCE**: Menganalisis elemen visual...", parse_mode="Markdown")
    try:
        file_info = bot.get_file(msg.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("../logs/temp_vision.png", "wb") as new_file:
            new_file.write(downloaded_file)
        
        # Import dynamically to avoid circular issues
        import sys
        sys.path.append(os.path.dirname(__file__))
        from vision_analyzer import ScreenVisionIntelligence
        
        result = ScreenVisionIntelligence.analyze_screen("../logs/temp_vision.png")
        bot.reply_to(msg, f"📊 **ANALISIS VISUAL**:\n`{json.dumps(result, indent=2)}`", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(msg, f"❌ Vision Error: {e}")

@bot.message_handler(func=lambda m: True)
def handle_all(msg):
    if not is_authorized(msg):
        bot.reply_to(msg, "⛔ Akses ditolak.")
        return

    raw_text = msg.text.strip()
    bot.send_chat_action(msg.chat.id, "typing")

    # 0. NLU Normalization (Elite Sovereign NLU)
    nlu_result = NLUProcessor.normalize_input(raw_text)
    text = nlu_result["normalized"].lower()
    intent = nlu_result["intent"]
    
    log.info(f"✨ NLU Normalized: {raw_text} -> {text} (Intent: {intent})")

    # 1. Rule-Based Intent Mapping (Using Normalized Text)
    mapping = {
        "screenshot": "screenshot", "foto": "screenshot", "ss": "screenshot", "layar": "screenshot",
        "battery": "battery", "baterai": "battery", "power": "battery", "persen": "battery",
        "info": "info", "status": "info", "manifest": "info",
        "reboot": "shell", "restart": "shell"
    }

    found_action = None
    for key, action in mapping.items():
        if key in text:
            found_action = action
            break

    if found_action:
        params = {"cmd": "reboot"} if found_action == "shell" and "reboot" in text else {}
        r = cloud_cmd(found_action, params=params, desc=f"Telegram Quick: {text}")
        bot.reply_to(msg, f"💠 **ELITE EXECUTION**: `{found_action.upper()}`\nStatus: `{r.get('status', 'QUEUED')}`", parse_mode="Markdown")
        return

    # 2. Dynamic Skill Execution
    skills = SkillAcquisitionEngine.get_integrated_skills()
    for s_name in skills:
        if s_name.lower() in text:
            bot.reply_to(msg, f"🚀 **DYNAMIC EXECUTION**: Menggunakan skill `{s_name}`...")
            result = SkillAcquisitionEngine.execute_skill(s_name, text)
            bot.reply_to(msg, f"📊 **RESULT**:\n`{json.dumps(result, indent=2)}`", parse_mode="Markdown")
            return

    # 3. AI Processing (Brain Integration v14.0 with NLU Context)
    log.info(f"🧠 Querying Brain for: {text}")
    try:
        # Pass normalized context to Brain
        ai_resp = AIRouter.smart_query(
            f"USER INPUT (Normalized): {text}\n"
            f"INTENT: {intent}\n"
            f"ENTITIES: {json.dumps(nlu_result['entities'])}\n\n"
            f"INSTRUCTION: Respond in Indonesian as Noir Sovereign. Be efficient."
        )
        
        # Check for Actions in AI Response
        actions_found = re.findall(r'\[ACTION:(.*?)\]', ai_resp)
        for action_str in actions_found:
            parts = action_str.split(",")
            a_type = parts[0].strip()
            a_params = {}
            if "cmd=" in action_str:
                cmd_match = re.search(r'cmd="(.*?)"', action_str)
                if cmd_match: a_params["cmd"] = cmd_match.group(1)
            
            cloud_cmd(a_type, params=a_params, desc=f"AI Autonomous: {text}")

        # Clean the response from tags
        clean_resp = re.sub(r'\[ACTION:.*?\]', '', ai_resp).strip()
        bot.reply_to(msg, clean_resp or "Perintah diproses secara otonom.")
    except Exception as e:
        log.error(f"Brain Sync Error: {e}")
        bot.reply_to(msg, "⚠️ Brain Sync Error. Menggunakan mode darurat...")

if __name__ == "__main__":
    log.info("🖤 Noir Sovereign Telegram Bot — Starting...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
