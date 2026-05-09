import telebot
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

USDT_WALLET = "TXPVUxWLCtrm5JCkb9FX7LSjvbDmgnqj97"
PRICE = 0.01

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "Привет 👋\n\n"
        "💳 Доступ к приватке — 0.01 USDT (TRC20)\n"
        "Напиши /buy для оплаты"
    )

@bot.message_handler(commands=['buy'])
def buy(message):
    bot.send_message(message.chat.id,
        f"💳 Оплата:\n\n"
        f"Отправь {PRICE} USDT (TRC20)\n\n"
        f"📥 Адрес:\n`{USDT_WALLET}`\n\n"
        f"После оплаты напиши /paid",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['paid'])
def paid(message):
    bot.send_message(message.chat.id,
        "⏳ Проверка оплаты...\n"
        "Если всё ок — доступ будет выдан ✔️"
    )

bot.infinity_polling()