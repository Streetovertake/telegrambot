import telebot
import os
from datetime import datetime, timedelta
import threading
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------------- BOT INIT ----------------
TOKEN = os.environ["TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
CHANNEL_ID = os.environ["CHANNEL_ID"]
USDT_WALLET = os.environ["USDT_WALLET"]
DEMO_LINK = os.environ["DEMO_LINK"]

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

# ---------------- MENU ----------------
@bot.callback_query_handler(func=lambda call: call.data == "menu")
def menu(call):
    bot.answer_callback_query(call.id)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📊 ПРОВЕРКА ПОДПИСКИ", callback_data="check"))
    markup.add(InlineKeyboardButton("🔞 БЕСПЛАТНЫЙ РАЗОГРЕВ", callback_data="trial"))
    markup.add(InlineKeyboardButton("🏠 ВАРИАНТЫ ПОДПИСОК:3", callback_data="back"))

    bot.edit_message_text(
        "📱 <b>МЕНЮ НАВИГАЦИИ В БОТЕ</b>\n\n<i>Выбери нужный раздел</i>",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
        reply_markup=markup
    )

# ---------------- SHOW PLAN ----------------
def show_plan(call, title, desc, price, plan_key):

    user_state[call.from_user.id] = plan_key

    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton("💳 Банковская карта. Перевод.", callback_data=f"pay_card_{plan_key}"))
    markup.add(InlineKeyboardButton("🚀 СБП, Картой через Boosty ", callback_data=f"pay_boosty_{plan_key}"))
    markup.add(InlineKeyboardButton("💰 USDT (TRC20)", callback_data=f"pay_usdt_{plan_key}"))
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back_to_tariffs"))

    text = (
        f"🔥 <b>{title}</b>\n\n"
        f"{desc}\n\n"
        f"💸 <b>Цена: {price}₽</b>\n\n"
        f"<i>Выбери способ оплаты</i>"
    )

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
        reply_markup=markup
    )

# ---------------- BUY HANDLER ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy(call):

    plan_key = call.data.replace("buy_", "", 1)

    if plan_key not in PLANS:
        bot.send_message(call.from_user.id, "Ошибка тарифа")
        return

    if plan_key == "basic":
        buy_basic(call)
    elif plan_key == "middle":
        buy_middle(call)
    elif plan_key == "hot":
        buy_hot(call)
    elif plan_key == "ahhh":
        buy_ahhh(call)

# ---------------- PLANS BUTTONS ----------------
@bot.callback_query_handler(func=lambda call: call.data == "buy_basic")
def buy_basic(call):
    show_plan(call,
        "Basic / 1 день",
        "❤️ <i>Доступ на 24 часа в сладенький контент из подписки HOT</i>❤️\n\n"
        "❤️ <i>Красивые фотосессии в сочных косплеях</i>!\n\n"
        "❤️ <i>Короткие вертикальные видео БЕЗ ЦЕНЗУРЫ</i>\n\n"
        "😔 <i>Минусы: Без доступа к чатику</i>",
        600,
        "basic"
    )

@bot.callback_query_handler(func=lambda call: call.data == "buy_middle")
def buy_middle(call):
    show_plan(call,
        "Middle / 1 неделя",
        "❤️ <i>Доступ на <b>7 дней</b> в сладенький контент</i>",
        1600,
        "middle"
    )

@bot.callback_query_handler(func=lambda call: call.data == "buy_hot")
def buy_hot(call):
    show_plan(call,
        "HOT / 1 месяц",
        "❤️ <i>Доступ на 30 дней</i>",
        2500,
        "hot"
    )

@bot.callback_query_handler(func=lambda call: call.data == "buy_ahhh")
def buy_ahhh(call):
    show_plan(call,
        "Ahhh... VIP",
        "🥵 <b>САМЫЙ ГОРЯЧИЙ КОНТЕНТ</b>",
        4990,
        "ahhh"
    )

# ---------------- PAYMENTS ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_usdt"))
def pay_usdt(call):

    plan = user_state.get(call.from_user.id)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data=f"back_plan_{plan}"))
    markup.add(InlineKeyboardButton("✅ Я оплатил", callback_data="paid"))

    bot.edit_message_text(
        f"💰 USDT:\n<code>{USDT_WALLET}</code>",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_card"))
def pay_card(call):

    plan = user_state.get(call.from_user.id)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data=f"back_plan_{plan}"))
    markup.add(InlineKeyboardButton("✅ Я оплатил", callback_data="paid"))

    bot.edit_message_text(
        "💳 Оплата картой\n\n<code>2202228406930000</code>",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_boosty"))
def pay_boosty(call):

    plan = user_state.get(call.from_user.id)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data=f"back_plan_{plan}"))
    markup.add(InlineKeyboardButton("✅ Я оплатил", callback_data="paid"))

    bot.edit_message_text(
        "🚀 Boosty оплата\n<code>ссылка</code>",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
        reply_markup=markup
    )

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
        f"💰 ОПЛАТА\nUser: {user_id}\nPlan: {plan}\n\n/confirm_{user_id}"
    )

# ---------------- CONFIRM ----------------
@bot.message_handler(commands=['confirm'])
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

# ---------------- BACK ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("back_plan_"))
def back_plan(call):

    plan = call.data.replace("back_plan_", "")

    if plan == "basic":
        buy_basic(call)
    elif plan == "middle":
        buy_middle(call)
    elif plan == "hot":
        buy_hot(call)
    elif plan == "ahhh":
        buy_ahhh(call)

# ---------------- TARIFS ----------------
def show_tariffs(chat_id, message_id=None):

    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton("💙 Basic / 1 DAY", callback_data="buy_basic"))
    markup.add(InlineKeyboardButton("💛 Middle / 1 WEEK", callback_data="buy_middle"))
    markup.add(InlineKeyboardButton("❤️ HOT / 1 MONTH", callback_data="buy_hot"))
    markup.add(InlineKeyboardButton("🔥 Ahhh... V.I.P.", callback_data="buy_ahhh"))

    text = "🌭 <b>Привет, зайчик...</b>"

    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")

# ---------------- RUN ----------------
bot.infinity_polling()