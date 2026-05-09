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
user_state = {}
pending_payments = {}

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
    show_tariffs(message.chat.id)

# ---------------- TARIFS ----------------
def show_tariffs(chat_id, message_id=None):

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💙 Basic", callback_data="buy_basic"))
    markup.add(InlineKeyboardButton("💛 Middle", callback_data="buy_middle"))
    markup.add(InlineKeyboardButton("❤️ HOT", callback_data="buy_hot"))
    markup.add(InlineKeyboardButton("🔥 VIP", callback_data="buy_ahhh"))

    text = "🌭 <b>Выбери тариф</b>"

    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")

# ---------------- SHOW PLAN ----------------
def show_plan(call, plan_key):

    plan = PLANS[plan_key]
    user_state[call.from_user.id] = plan_key

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💳 Карта", callback_data=f"pay_card_{plan_key}"))
    markup.add(InlineKeyboardButton("🚀 Boosty", callback_data=f"pay_boosty_{plan_key}"))
    markup.add(InlineKeyboardButton("💰 USDT", callback_data=f"pay_usdt_{plan_key}"))
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    text = (
        f"🔥 <b>{plan['title']}</b>\n\n"
        f"💸 Цена: {plan['price']}₽\n\n"
        f"Выбери оплату"
    )

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=markup, parse_mode="HTML")

# ---------------- BUY ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy(call):

    plan_key = call.data.replace("buy_", "")

    if plan_key not in PLANS:
        bot.send_message(call.message.chat.id, "Ошибка тарифа")
        return

    show_plan(call, plan_key)

# ---------------- PAY ----------------
def pay_screen(call, method):

    plan = user_state.get(call.from_user.id)

    if not plan:
        bot.send_message(call.message.chat.id, "Ошибка: выбери тариф заново")
        return

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data=f"back_{plan}"))
    markup.add(InlineKeyboardButton("✅ Я оплатил", callback_data="paid"))

    if method == "usdt":
        text = f"💰 USDT:\n<code>{USDT_WALLET}</code>"

    elif method == "card":
        text = "💳 Перевод на карту:\n<code>2202228406930000</code>"

    else:
        text = "🚀 Boosty оплата"

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=markup, parse_mode="HTML")

# ---------------- PAY HANDLERS ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_usdt"))
def pay_usdt(call):
    pay_screen(call, "usdt")

@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_card"))
def pay_card(call):
    pay_screen(call, "card")

@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_boosty"))
def pay_boosty(call):
    pay_screen(call, "boosty")

# ---------------- BACK ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("back_"))
def back(call):

    plan = call.data.replace("back_", "")

    show_plan(call, plan)

# ---------------- PAID ----------------
@bot.callback_query_handler(func=lambda call: call.data == "paid")
def paid(call):

    user_id = call.from_user.id
    plan = user_state.get(user_id)

    if not plan:
        bot.send_message(user_id, "Ошибка: нет тарифа")
        return

    pending_payments[user_id] = plan

    bot.send_message(
        ADMIN_ID,
        f"💰 ОПЛАТА\nUser: {user_id}\nPlan: {plan}\n\nНажми: /confirm_{user_id}"
    )

# ---------------- CONFIRM ----------------
@bot.message_handler(func=lambda m: m.text and m.text.startswith("/confirm_"))
def confirm(message):

    if message.from_user.id != ADMIN_ID:
        return

    user_id = int(message.text.split("_")[1])

    plan = pending_payments.get(user_id)

    if not plan:
        bot.send_message(ADMIN_ID, "Нет заявки")
        return

    subs[user_id] = {
        "expire": datetime.now() + timedelta(days=PLANS[plan]["days"]),
        "plan": plan
    }

    bot.send_message(user_id, "✅ Оплата подтверждена 🔥")

    del pending_payments[user_id]

# ---------------- RUN ----------------
bot.infinity_polling()