import telebot
import os
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ["TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
USDT_WALLET = os.environ["USDT_WALLET"]

bot = telebot.TeleBot(TOKEN)

# ---------------- STORAGE ----------------
subs = {}
pending_payments = {}
user_state = {}
nav_stack = {}

# ---------------- STACK ----------------
def push(user_id, state):
    nav_stack.setdefault(user_id, []).append(state)

def pop(user_id):
    if nav_stack.get(user_id):
        return nav_stack[user_id].pop()
    return None

# ---------------- PLANS ----------------
PLANS = {
    "basic": {"days": 1, "price": 600, "title": "Basic"},
    "middle": {"days": 7, "price": 1600, "title": "Middle"},
    "hot": {"days": 30, "price": 2500, "title": "HOT"},
    "ahhh": {"days": 30, "price": 4990, "title": "Ahhh"}
}

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    show_menu(message.chat.id)
    push(message.chat.id, "menu")

# ---------------- MENU ----------------
def show_menu(chat_id, message_id=None):

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📊 Проверить подписку", callback_data="check_sub"))
    markup.add(InlineKeyboardButton("🎥 Тестовое видео", callback_data="trial_video"))
    markup.add(InlineKeyboardButton("💰 Список тарифов", callback_data="tariffs"))

    text = "📱 <b>МЕНЮ</b>"

    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")

# ---------------- TARIFS ----------------
def show_tariffs(chat_id, message_id=None):

    push(chat_id, "tariffs")

    markup = InlineKeyboardMarkup()

    for k, v in PLANS.items():
        markup.add(InlineKeyboardButton(
            f"{v['title']} / {v['price']}₽",
            callback_data=f"plan_{k}"
        ))

    text = "💰 <b>Выбери тариф</b>"

    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")

# ---------------- PLAN ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("plan_"))
def plan(call):

    user_id = call.from_user.id
    plan_key = call.data.split("_")[1]

    if plan_key not in PLANS:
        return

    user_state[user_id] = plan_key
    push(user_id, f"plan_{plan_key}")

    show_plan(call, plan_key)

# ---------------- SHOW PLAN ----------------
def show_plan(call, plan_key):

    plan = PLANS[plan_key]

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💳 Карта", callback_data=f"card_{plan_key}"))
    markup.add(InlineKeyboardButton("💰 USDT", callback_data=f"usdt_{plan_key}"))
    markup.add(InlineKeyboardButton("🚀 Boosty", callback_data=f"boosty_{plan_key}"))
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    bot.edit_message_text(
        f"🔥 <b>{plan['title']}</b>\n💸 {plan['price']}₽",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode="HTML"
    )

# ---------------- TEST VIDEO ----------------
@bot.callback_query_handler(func=lambda call: call.data == "trial_video")
def trial_video(call):

    push(call.from_user.id, "trial")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    bot.edit_message_text(
        "🎬 Тестовое видео\n(сюда вставишь ссылку или канал)",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# ---------------- PAY SCREEN ----------------
def pay(call, method, plan_key):

    user_state[call.from_user.id] = plan_key

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))
    markup.add(InlineKeyboardButton("✅ Я оплатил", callback_data=f"paid_{method}_{plan_key}"))

    if method == "usdt":
        text = f"💰 USDT:\n<code>{USDT_WALLET}</code>"
    elif method == "card":
        text = "💳 Карта:\n<code>2202...</code>"
    else:
        text = "🚀 Boosty"

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode="HTML"
    )

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
@bot.callback_query_handler(func=lambda call: call.data.startswith("paid_"))
def paid(call):

    parts = call.data.split("_")
    method = parts[1]
    plan_key = parts[2]

    user_id = call.from_user.id

    pending_payments[user_id] = {
        "plan": plan_key,
        "method": method
    }

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{user_id}"))

    bot.send_message(
        ADMIN_ID,
        f"💰 PAYMENT\nUser: {user_id}\nPlan: {plan_key}\nMethod: {method}",
        reply_markup=markup
    )

# ---------------- CONFIRM ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm(call):

    if call.from_user.id != ADMIN_ID:
        return

    user_id = int(call.data.split("_")[1])

    data = pending_payments.get(user_id)
    if not data:
        return

    plan = PLANS[data["plan"]]

    subs[user_id] = {
        "expire": datetime.now() + timedelta(days=plan["days"]),
        "plan": data["plan"]
    }

    bot.send_message(user_id, "✅ Оплата подтверждена 🔥")
    bot.send_message(ADMIN_ID, "Готово")

    pending_payments.pop(user_id, None)

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
        show_plan(call, plan_key)

    else:
        show_menu(call.message.chat.id, call.message.message_id)

# ---------------- RUN ----------------
print("BOT STARTED")
bot.infinity_polling(skip_pending=True)