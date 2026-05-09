import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# 👇 ссылки на приватки
PRIVATE_1 = "https://t.me/+link1"
PRIVATE_2 = "https://t.me/+link2"

USDT_WALLET = "ТВОЙ_USDT_АДРЕС"
PRICE = 5

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()

    btn = InlineKeyboardButton("💳 Купить доступ", callback_data="buy")
    markup.add(btn)

    bot.send_message(message.chat.id,
        "👋 Привет!\nВыбери действие:",
        reply_markup=markup
    )

# ---------------- BUY MENU ----------------
@bot.callback_query_handler(func=lambda call: call.data == "buy")
def buy_menu(call):
    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton("🔥 Приватка 1", callback_data="p1"))
    markup.add(InlineKeyboardButton("🔥 Приватка 2", callback_data="p2"))

    bot.edit_message_text(
        "Выбери доступ:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# ---------------- PRIVATE 1 ----------------
@bot.callback_query_handler(func=lambda call: call.data == "p1")
def private1(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💰 Оплатить USDT", callback_data="pay1"))

    bot.edit_message_text(
        "🔥 Приватка 1 — 5 USDT",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# ---------------- PRIVATE 2 ----------------
@bot.callback_query_handler(func=lambda call: call.data == "p2")
def private2(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💰 Оплатить USDT", callback_data="pay2"))

    bot.edit_message_text(
        "🔥 Приватка 2 — 5 USDT",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# ---------------- PAYMENT ----------------
@bot.callback_query_handler(func=lambda call: call.data in ["pay1", "pay2"])
def pay(call):
    bot.send_message(call.message.chat.id,
        f"💳 Отправь {PRICE} USDT (TRC20)\n\n"
        f"📥 Адрес:\n`{USDT_WALLET}`\n\n"
        f"После оплаты напиши /paid",
        parse_mode="Markdown"
    )

# ---------------- PAID (пока вручную) ----------------
@bot.callback_query_handler(func=lambda call: call.data == "paid")
def paid(call):
    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton("📌 Приватка 1", url=PRIVATE_1))
    markup.add(InlineKeyboardButton("📌 Приватка 2", url=PRIVATE_2))

    bot.send_message(call.message.chat.id,
        "✔ Проверка оплаты...\n\n"
        "Если всё ок — вот доступ 👇",
        reply_markup=markup
    )
bot.infinity_polling()