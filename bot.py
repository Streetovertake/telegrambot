import telebot
import os
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------------- INIT ----------------
TOKEN = os.environ["TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
USDT_WALLET = os.environ["USDT_WALLET"]

bot = telebot.TeleBot(TOKEN)

# ---------------- STORAGE ----------------
subs = {}
pending_payments = {}
user_state = {}
nav_stack = {}

# ---------------- PLANS ----------------
PLANS = {
    "basic": {"days": 1, "price": 600, "title": "Basic"},
    "middle": {"days": 7, "price": 1600, "title": "Middle"},
    "hot": {"days": 30, "price": 2500, "title": "HOT"},
    "ahhh": {"days": 30, "price": 4990, "title": "Ahhh"}
}

# ---------------- NAV STACK ----------------
def push(uid, state):
    nav_stack.setdefault(uid, []).append(state)

def pop(uid):
    return nav_stack.get(uid, []).pop() if nav_stack.get(uid) else None

# ---------------- SAFE EDIT ----------------
def safe_edit(call, text, markup=None):
    try:
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="HTML"
        )
    except:
        pass

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    show_menu(message.chat.id)

# ---------------- MENU ----------------
def show_menu(chat_id, message_id=None):

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📊 Проверить подписку", callback_data="check"))
    markup.add(InlineKeyboardButton("🎥 Тестовое видео", callback_data="trial"))
    markup.add(InlineKeyboardButton("💰 Список тарифов", callback_data="tariffs"))

    text = "📱 <b>МЕНЮ</b>"

    try:
        if message_id:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
        else:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    except:
        pass

# ---------------- TARIFS ----------------
def show_tariffs(chat_id, message_id=None, user_id=None):

    if user_id:
        push(user_id, "menu")

    markup = InlineKeyboardMarkup()

    for k, v in PLANS.items():
        markup.add(InlineKeyboardButton(
            f"{v['title']} / {v['price']}₽",
            callback_data=f"plan_{k}"
        ))

    text = "💰 <b>Выбери тариф</b>"

    try:
        if message_id:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
        else:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    except:
        pass

# ---------------- PLAN OPEN ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("plan_"))
def plan(call):

    user_id = call.from_user.id
    plan_key = call.data.split("_")[1]

    if plan_key not in PLANS:
        return

    user_state[user_id] = plan_key
    push(user_id, "tariffs")

    plan = PLANS[plan_key]

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💳 Карта", callback_data=f"card_{plan_key}"))
    markup.add(InlineKeyboardButton("💰 USDT", callback_data=f"usdt_{plan_key}"))
    markup.add(InlineKeyboardButton("🚀 Boosty", callback_data=f"boosty_{plan_key}"))
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    text = f"🔥 <b>{plan['title']}</b>\n💸 {plan['price']}₽"

    safe_edit(call, text, markup)

# ---------------- PAY SCREEN ----------------
def pay(call, method, plan_key):

    plan = PLANS.get(plan_key)
    if not plan:
        return

    user_id = call.from_user.id
    user_state[user_id] = plan_key

    push(user_id, f"plan_{plan_key}")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))
    markup.add(InlineKeyboardButton("✅ Я оплатил", callback_data="paid"))

    if method == "usdt":
        text = f"💰 USDT:\n<code>{USDT_WALLET}</code>"
    elif method == "card":
        text = "💳 Карта:\n<code>2202....</code>"
    else:
        text = "🚀 Boosty ссылка"

    safe_edit(call, text, markup)

# ---------------- PAY HANDLERS ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("usdt_"))
def usdt(call):
    pay(call, "usdt", call.data.split("_")[1])

@bot.callback_query_handler(func=lambda call: call.data.startswith("card_"))
def card(call):
    pay(call, "card", call.data.split("_")[1])

@bot.callback_query_handler(func=lambda call: call.data.startswith("boosty_"))
def boosty(call):
    pay(call, "boosty", call.data.split("_")[1])

# ---------------- PAID ----------------
@bot.callback_query_handler(func=lambda call: call.data == "paid")
def paid(call):

    user_id = call.from_user.id
    plan = user_state.get(user_id)

    if not plan:
        bot.send_message(user_id, "Ошибка")
        return

    pending_payments[user_id] = plan

    bot.send_message(
        ADMIN_ID,
        f"💰 ОПЛАТА\nUser: {user_id}\nPlan: {plan}"
    )

# ---------------- BACK ----------------
@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):

    user_id = call.from_user.id
    prev = pop(user_id)

    if not prev:
        show_menu(call.message.chat.id, call.message.message_id)
        return

    if prev == "menu":
        show_menu(call.message.chat.id, call.message.message_id)

    elif prev == "tariffs":
        show_tariffs(call.message.chat.id, call.message.message_id)

    elif prev.startswith("plan_"):
        plan_key = prev.split("_")[1]
        plan(call, plan_key)

# ---------------- TRIAL ----------------
@bot.callback_query_handler(func=lambda call: call.data == "trial")
def trial(call):

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    safe_edit(call,
        "🎥 Тестовое видео (сюда вставишь ссылку/канал)",
        markup
    )

# ---------------- RUN ----------------
print("BOT STARTED")
bot.infinity_polling(skip_pending=True)