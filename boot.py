import telebot
from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
import json, os, re, threading, time, requests
from flask import Flask

# ══════════════════════════════════════════
#  FLASK — FAKE PORT (RENDER)
# ══════════════════════════════════════════
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ zadxpro Bot is running!", 200

@app.route("/health")
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True)

# ══════════════════════════════════════════
#  KEEP-ALIVE — ҳар 1 дақиқа пинг
# ══════════════════════════════════════════
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "")

def keep_alive():
    time.sleep(30)  # Аввал 30 сония интизор шав то Flask бала ояд
    while True:
        if RENDER_URL:
            try:
                r = requests.get(RENDER_URL + "/health", timeout=10)
                print(f"[KeepAlive] ✅ ping → {r.status_code}")
            except Exception as e:
                print(f"[KeepAlive] ❌ xato: {e}")
        time.sleep(60)  # 1 дақиқа

# ══════════════════════════════════════════
#  ТАНЗИМОТ
# ══════════════════════════════════════════
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8764205211:AAEBhZe3gz3NhNZdbckF71IP7Ih3PqJmANQ")
ADMIN_ID  = 7424107874
CHANNELS  = ["@zadxpro_film", "@zadxproooo"]

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

USERS_FILE      = "users.json"
pending_phone   = {}
broadcast_state = {}

# ══════════════════════════════════════════
#  БАЗАИ ЮЗЕРОН
# ══════════════════════════════════════════
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    return []

def save_user(uid):
    users = load_users()
    if uid not in users:
        users.append(uid)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

# ══════════════════════════════════════════
#  ТАФТИШИ ОБУНА
# ══════════════════════════════════════════
def check_subscribe(uid):
    for ch in CHANNELS:
        try:
            m = bot.get_chat_member(ch, uid)
            if m.status not in ["member", "administrator", "creator"]:
                return False, ch
        except:
            return False, ch
    return True, None

def sub_keyboard():
    kb = InlineKeyboardMarkup()
    for ch in CHANNELS:
        label = "🎬  Канали филм" if "film" in ch else "💻  Канали асосӣ"
        kb.add(InlineKeyboardButton(f"{label}  |  {ch}",
               url=f"https://t.me/{ch.replace('@','')}"))
    kb.add(InlineKeyboardButton("✅  Обуна шудам — тафтиш кун", callback_data="check_sub"))
    return kb

# ══════════════════════════════════════════
#  ТАФТИШИ РАҚАМИ ТОҶИКӢ
# ══════════════════════════════════════════
def is_tajik_number(phone: str) -> bool:
    phone = re.sub(r"[\s\-\(\)]", "", phone)
    return bool(re.match(r"^\+?992\d{9}$", phone))

def phone_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("📱  Рақами худро фиристодан", request_contact=True))
    return kb

# ══════════════════════════════════════════
#  КЛАВИАТУРАҲО
# ══════════════════════════════════════════
def main_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🤖  Ботҳои мо",   callback_data="our_bots"),
        InlineKeyboardButton("💰  Нархнома",     callback_data="prices"),
    )
    kb.add(
        InlineKeyboardButton("✨  Намунаҳо",     callback_data="examples"),
        InlineKeyboardButton("🏆  Чаро мо?",     callback_data="why_us"),
    )
    kb.add(InlineKeyboardButton("📲  Фармоиш додан", callback_data="order"))
    return kb

def back_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔙  Бозгашт", callback_data="back_main"))
    return kb

def back_order_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📲  Фармоиш",  callback_data="order"),
        InlineKeyboardButton("🔙  Бозгашт",  callback_data="back_main"),
    )
    return kb

# ══════════════════════════════════════════
#  МАТНҲО
# ══════════════════════════════════════════
MAIN_TEXT = """
╔═══════════════════════════╗
    ⚡ *Z A D X P R O*  ⚡
       🤖  *Bot  Studio*
╚═══════════════════════════╝

Салом, *{name}*! 👋🏻

Мо ботҳои Telegram месозем —
касбӣ, зебо ва бо гарантия ✅

Ба *ҳазорон* одам расонидани
паём, фурӯш ва хизмат танҳо
бо як бот имконпазир аст 🚀

━━━━━━━━━━━━━━━━━━━━━━━
👇🏻  Гузинаро интихоб кун
"""

BOTS_TEXT = """
🤖  *Б о т ҳ о и   м о*
━━━━━━━━━━━━━━━━━━━━━━━

Мо *ҳар намуди* бот месозем —
агар қонунӣ бошад, мешавад! ✅

🛍  *Бот барои дӯкон*
     Каталог · сабад · фармоиш онлайн

📢  *Бот барои обуна*
     Тафтиши канал · линкҳои автоматӣ

📋  *Бот-анкета*
     Саволнома · ҷамъоварии маълумот

📝  *Бот барои тест*
     Саволу ҷавоб · аттестат · натиҷа

📣  *Бот барои broadcast*
     Паёмрасонии оммавӣ ба ҳазорон нафар

📅  *Бот барои захира*
     Навбат · вақт · ёдоварӣ автоматӣ

🤖  *Бот бо AI (ChatGPT)*
     Ҷавоби зиракона ба ҳар савол

🍽  *Бот барои ресторан*
     Меню · фармоиш онлайн · таҳвил

🚖  *Бот барои такси*
     Захира · ронандагон · нарх авто

💎  *Бот барои реферал*
     Бонус · рейтинг · маркетинг

━━━━━━━━━━━━━━━━━━━━━━━
💬 Агар идеяи дигар дорӣ — гӯ,
мо имконоти онро месанҷем!
"""

PRICES_TEXT = """
💰  *Н а р х н о м а*
━━━━━━━━━━━━━━━━━━━━━━━

Нарх аз *ҳаҷми кор* вобаста аст:

🟢  *Хурд*  —  аз  *100 сомонӣ*
     Ботҳои оддӣ, 1–2 функсия
     (мис: обуна, анкета, линк)

🟡  *Миёна*  —  аз  *300 сомонӣ*
     Функсияҳои зиёд + панели админ
     (мис: дӯкон, тест, broadcast)

🔴  *Калон*  —  аз  *600 сомонӣ*
     Системаҳои мураккаб, AI, CRM
     (мис: такси, ресторан, реферал)

━━━━━━━━━━━━━━━━━━━━━━━
✅  *Дар ҳама нарх дохил аст:*
    Насб ба сервер
    Дастурамали истифода
    Дастгирии 1 моҳ ройгон
    Тағйироти хурд ройгон

📌 Нарх дақиқ пас аз муҳокима
муайян карда мешавад
"""

EXAMPLES_TEXT = (
    "\n"
    "✨  Н а м у н а ҳ о\n"
    "━━━━━━━━━━━━━━━━━━━━━━━\n"
    "\n"
    "Ботҳои кории мо 👇🏻\n"
    "\n"
    "🎬  Канали филм:\n"
    "     @zadxpro_film\n"
    "\n"
    "💻  Канали асосӣ:\n"
    "     @zadxproooo\n"
    "\n"
    "━━━━━━━━━━━━━━━━━━━━━━━\n"
    "🔔 Ботҳои нав ва намунаҳоро\n"
    "аввалин дар каналҳо нашр мекунем!\n"
    "\n"
    "💬 Мехоҳӣ демо бинӣ?\n"
    "Бо мо тамос гир — нишон медиҳем!\n"
)

WHY_TEXT = """
🏆  *Ч а р о   м а ъ з а н   м о ?*
━━━━━━━━━━━━━━━━━━━━━━━

⚡  *Зудӣ*
     Бот дар 1–3 рӯз таҳвил дода мешавад

💎  *Сифат*
     Код тоза, бот мустаҳкам ва зебо

💰  *Нарх*
     Аз рақибон арзонтар, бо гарантия

🛡  *Гарантия*
     1 моҳ дастгирии ройгон пас аз таҳвил

🗣  *Маҳаллӣ*
     Тоҷик, забони худро медонем

🎯  *Дастгирӣ*
     Ҳар хатогӣ — ройгон ислоҳ мешавад

━━━━━━━━━━━━━━━━━━━━━━━
💬  *Чӣ мегӯянд муштариёни мо:*

"Зуд, арзон, бе ташвиш!"

"Бот барои дӯконам фурӯшро зиёд кард!"

"Аз ҳама беҳтарин дар Тоҷикистон!"
"""

ORDER_TEXT = """
📲  *Ф а р м о и ш   д о д а н*
━━━━━━━━━━━━━━━━━━━━━━━

Барои фармоиш ин ҷо навис 👇🏻

👤  *Соҳиб:*  @zadxpr0

━━━━━━━━━━━━━━━━━━━━━━━
📝  *Дар паём нависед:*

1  Чӣ намуд бот лозим аст?
2  Кадом функсияҳо?
3  Муддати таҳвил?

━━━━━━━━━━━━━━━━━━━━━━━
Дар 1 соат ҷавоб медиҳем!
"""

# ══════════════════════════════════════════
#  ЁРДАМЧИИ EDIT
# ══════════════════════════════════════════
def edit_or_send(chat_id, msg_id, text, kb, parse_mode="Markdown"):
    try:
        bot.edit_message_text(text, chat_id, msg_id,
                              parse_mode=parse_mode, reply_markup=kb)
    except:
        bot.send_message(chat_id, text, parse_mode=parse_mode, reply_markup=kb)

# ══════════════════════════════════════════
#  /start
# ══════════════════════════════════════════
@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id
    save_user(uid)
    ok, ch = check_subscribe(uid)
    if not ok:
        bot.send_message(
            uid,
            "🔔  *Барои истифода аввал обуна шав!*\n\n"
            "Ба ҳар 2 канал обуна шав,\n"
            "баъд *Тафтиш* -ро зан 👇🏻",
            parse_mode="Markdown",
            reply_markup=sub_keyboard()
        )
        return
    pending_phone[uid] = True
    bot.send_message(
        uid,
        "📱  *Рақами телефонатро тасдиқ кун*\n\n"
        "Тугмаи зеринро зан 👇🏻",
        parse_mode="Markdown",
        reply_markup=phone_kb()
    )

@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def cb_check_sub(call):
    uid = call.from_user.id
    ok, ch = check_subscribe(uid)
    if ok:
        bot.answer_callback_query(call.id, "✅ Ташаккур! Обуна тасдиқ шуд!")
        try:
            bot.delete_message(uid, call.message.message_id)
        except:
            pass
        pending_phone[uid] = True
        bot.send_message(
            uid,
            "📱  *Рақами телефонатро тасдиқ кун*\n\n"
            "Тугмаи зеринро зан 👇🏻",
            parse_mode="Markdown",
            reply_markup=phone_kb()
        )
    else:
        bot.answer_callback_query(call.id,
            f"❌ Ҳанӯз обуна нашудед ба {ch}!", show_alert=True)

# ══════════════════════════════════════════
#  САНҶИШИ РАҚАМ
# ══════════════════════════════════════════
def welcome_user(uid, first_name):
    bot.send_message(uid, "✅  *Рақам тасдиқ шуд!*",
                     parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    bot.send_message(uid, MAIN_TEXT.format(name=first_name),
                     parse_mode="Markdown", reply_markup=main_kb())

@bot.message_handler(content_types=["contact"])
def handle_contact(message):
    uid = message.from_user.id
    if not pending_phone.get(uid):
        return
    if not is_tajik_number(message.contact.phone_number):
        bot.send_message(uid,
            "❌  *Рақами тоҷикӣ (+992) лозим аст!*\n\nДубора фирист 👇🏻",
            parse_mode="Markdown", reply_markup=phone_kb())
        return
    pending_phone.pop(uid, None)
    welcome_user(uid, message.from_user.first_name)

@bot.message_handler(func=lambda m: pending_phone.get(m.from_user.id))
def handle_text_phone(message):
    uid = message.from_user.id
    if is_tajik_number(message.text.strip()):
        pending_phone.pop(uid, None)
        welcome_user(uid, message.from_user.first_name)
    else:
        bot.send_message(uid,
            "❌  *Рақами тоҷикӣ (+992) лозим аст!*\n\nМисол: +992901234567",
            parse_mode="Markdown", reply_markup=phone_kb())

# ══════════════════════════════════════════
#  CALLBACK — МЕНЮ
# ══════════════════════════════════════════
@bot.callback_query_handler(func=lambda c: c.data == "back_main")
def cb_back(call):
    edit_or_send(call.message.chat.id, call.message.message_id,
                 MAIN_TEXT.format(name=call.from_user.first_name), main_kb())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "our_bots")
def cb_bots(call):
    edit_or_send(call.message.chat.id, call.message.message_id, BOTS_TEXT, back_order_kb())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "prices")
def cb_prices(call):
    edit_or_send(call.message.chat.id, call.message.message_id, PRICES_TEXT, back_order_kb())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "examples")
def cb_examples(call):
    edit_or_send(call.message.chat.id, call.message.message_id,
                 EXAMPLES_TEXT, back_order_kb(), parse_mode=None)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "why_us")
def cb_why(call):
    edit_or_send(call.message.chat.id, call.message.message_id, WHY_TEXT, back_order_kb())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "order")
def cb_order(call):
    edit_or_send(call.message.chat.id, call.message.message_id, ORDER_TEXT, back_kb())
    bot.answer_callback_query(call.id)

# ══════════════════════════════════════════
#  ПАНЕЛИ АДМИН
# ══════════════════════════════════════════
@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = load_users()
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📢  Broadcast", callback_data="bc_start"))
    kb.add(InlineKeyboardButton("👥  Шумораи юзерон", callback_data="bc_count"))
    bot.send_message(message.chat.id,
        f"🔐  *Панели Админ*\n\n👥  Юзерон: *{len(users)}* нафар",
        parse_mode="Markdown", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == "bc_count")
def cb_count(call):
    users = load_users()
    bot.answer_callback_query(call.id, f"👥 Ҷамъ: {len(users)} нафар", show_alert=True)

@bot.callback_query_handler(func=lambda c: c.data == "bc_start")
def cb_bc_start(call):
    if call.from_user.id != ADMIN_ID:
        return
    broadcast_state[call.from_user.id] = True
    bot.answer_callback_query(call.id)
    bot.send_message(call.from_user.id, "📢  Паёми broadcast-ро бинависед:")

@bot.message_handler(
    func=lambda m: broadcast_state.get(m.from_user.id),
    content_types=["text", "photo", "video", "document"]
)
def do_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    broadcast_state.pop(message.from_user.id, None)
    users = load_users()
    ok = fail = 0
    for uid in users:
        try:
            bot.copy_message(uid, message.chat.id, message.message_id)
            ok += 1
        except:
            fail += 1
    bot.send_message(message.chat.id,
        f"✅  Broadcast тамом!\n✔️  Расид: {ok}\n❌  Нарасид: {fail}")

# ══════════════════════════════════════════
#  ОҒОЗ — Flask + KeepAlive + Bot
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("⚡ zadxpro Bot оғоз ёфт!")

    # Flask дар thread-и алоҳида
    t_flask = threading.Thread(target=run_flask, daemon=True)
    t_flask.start()

    # KeepAlive дар thread-и алоҳида
    t_keep = threading.Thread(target=keep_alive, daemon=True)
    t_keep.start()

    # Бот бо restart_on_change дар thread-и асосӣ
    while True:
        try:
            print("🤖 Polling оғоз...")
            bot.infinity_polling(
                skip_pending=True,
                timeout=60,
                long_polling_timeout=60
            )
        except Exception as e:
            print(f"[Bot] ❌ Хато: {e} — 5 сония интизор...")
            time.sleep(5)
