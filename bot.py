import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

USDT_WALLET = "ТВОЙ_USDT_АДРЕС"

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    show_tariffs(message.chat.id)

# ---------------- MAIN MENU ----------------
def show_tariffs(chat_id, message_id=None):
    markup = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("💎 Для маменькиных сыночков", callback_data="tariff_soft")
    btn2 = InlineKeyboardButton("🔥 Для взрослых", callback_data="tariff_hard")
    menu_btn = InlineKeyboardButton("📱 Меню", callback_data="menu")

    markup.add(btn1)
    markup.add(btn2)
    markup.add(menu_btn)

    text = (
        "👁 Я знаю, зачем ты пришёл...\n"
        "I know why you're here...\n\n"
        "👇 Выбери тариф"
    )

    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)

# ---------------- TARIFF SOFT ----------------
@bot.callback_query_handler(func=lambda call: call.data == "tariff_soft")
def tariff_soft(call):
    markup = InlineKeyboardMarkup()

    btn_usdt = InlineKeyboardButton("💰 USDT", callback_data="pay_usdt_soft")
    btn_card = InlineKeyboardButton("💳 Карта банка", callback_data="pay_card_soft")
    btn_boosty = InlineKeyboardButton("🚀 Boosty", callback_data="pay_boosty_soft")
    back = InlineKeyboardButton("⬅ Назад", callback_data="back")

    markup.add(btn_usdt)
    markup.add(btn_card)
    markup.add(btn_boosty)
    markup.add(back)

    text = (
        "💎 Тариф: Для маменькиных сыночков\n\n"
        "📌 Описание (вставишь сам)\n"
        "💰 Цена: XX"
    )

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

# ---------------- TARIFF HARD ----------------
@bot.callback_query_handler(func=lambda call: call.data == "tariff_hard")
def tariff_hard(call):
    markup = InlineKeyboardMarkup()

    btn_usdt = InlineKeyboardButton("💰 USDT", callback_data="pay_usdt_hard")
    btn_card = InlineKeyboardButton("💳 Карта банка", callback_data="pay_card_hard")
    btn_boosty = InlineKeyboardButton("🚀 Boosty", callback_data="pay_boosty_hard")
    back = InlineKeyboardButton("⬅ Назад", callback_data="back")

    markup.add(btn_usdt)
    markup.add(btn_card)
    markup.add(btn_boosty)
    markup.add(back)

    text = (
        "🔥 Тариф: Для взрослых\n\n"
        "📌 Описание (вставишь сам)\n"
        "💰 Цена: XX"
    )

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

# ---------------- PAY USDT ----------------
@bot.callback_query_handler(func=lambda call: "pay_usdt" in call.data)
def pay_usdt(call):
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton("⬅ Назад", callback_data="back")

    markup.add(back)

    bot.send_message(call.message.chat.id,
        f"💰 Оплата USDT (TRC20)\n\n"
        f"📥 Адрес:\n`{USDT_WALLET}`\n\n"
        f"После оплаты нажми /paid",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ---------------- PAY CARD ----------------
@bot.callback_query_handler(func=lambda call: "pay_card" in call.data)
def pay_card(call):
    bot.send_message(call.message.chat.id,
        "💳 Оплата картой\n\n"
        "👉 Вставишь сюда реквизиты\n"
        "После оплаты нажми /paid"
    )

# ---------------- BOOSTY ----------------
@bot.callback_query_handler(func=lambda call: "pay_boosty" in call.data)
def pay_boosty(call):
    bot.send_message(call.message.chat.id,
        "🚀 Оплата через Boosty\n\n"
        "👉 Вставишь ссылку на Boosty подписку\n"
        "После оплаты нажми /paid"
    )

# ---------------- PAID (пока ручная выдача) ----------------
@bot.message_handler(commands=['paid'])
def paid(message):
    bot.send_message(message.chat.id,
        "✔ Оплата принята (проверка вручную)\n\n"
        "👉 Доступ выдан (вставишь ссылки на приватки)"
    )

# ---------------- MENU ----------------
@bot.callback_query_handler(func=lambda call: call.data == "menu")
def menu(call):
    markup = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("📊 Проверить подписку", callback_data="check")
    btn2 = InlineKeyboardButton("🎥 Пробное видео", callback_data="trial")
    btn3 = InlineKeyboardButton("🏠 Тарифы", callback_data="back")

    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)

    bot.edit_message_text("📱 Меню:", call.message.chat.id, call.message.message_id, reply_markup=markup)

# ---------------- CHECK / TRIAL ----------------
@bot.callback_query_handler(func=lambda call: call.data == "check")
def check(call):
    bot.send_message(call.message.chat.id, "⏳ Тут будет проверка подписки")

@bot.callback_query_handler(func=lambda call: call.data == "trial")
def trial(call):
    bot.send_message(call.message.chat.id, "🎥 Тут будет пробное видео")

# ---------------- BACK ----------------
@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    show_tariffs(call.message.chat.id, call.message.message_id)

# ---------------- RUN ----------------
bot.infinity_polling()