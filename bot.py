import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("💎 Для маменькиных сыночков", callback_data="soft")
    btn2 = InlineKeyboardButton("🔥 Для взрослых", callback_data="hard")

    markup.add(btn1)
    markup.add(btn2)

    text = (
        "👁 Я знаю, зачем ты пришёл...\n"
        "I know why you're here...\n\n"
        "👇 Выбери свой уровень доступа"
    )

    bot.send_message(message.chat.id, text, reply_markup=markup)

# ---------------- MAIN MENU BACK ----------------
def main_menu(chat_id, message_id=None):
    markup = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("💎 Для маменькиных сыночков", callback_data="soft")
    btn2 = InlineKeyboardButton("🔥 Для взрослых", callback_data="hard")

    markup.add(btn1)
    markup.add(btn2)

    text = "👁 Выбери уровень доступа"

    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)

# ---------------- SOFT TARIFF ----------------
@bot.callback_query_handler(func=lambda call: call.data == "soft")
def soft(call):
    markup = InlineKeyboardMarkup()

    back = InlineKeyboardButton("⬅ Назад", callback_data="back")
    markup.add(back)

    text = (
        "💎 Тариф: Для маменькиных сыночков\n\n"
        "📌 Описание добавишь сам\n"
        "💰 Цена: XX USDT"
    )

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

# ---------------- HARD TARIFF ----------------
@bot.callback_query_handler(func=lambda call: call.data == "hard")
def hard(call):
    markup = InlineKeyboardMarkup()

    back = InlineKeyboardButton("⬅ Назад", callback_data="back")
    markup.add(back)

    text = (
        "🔥 Тариф: Для взрослых\n\n"
        "📌 Описание добавишь сам\n"
        "💰 Цена: XX USDT"
    )

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

# ---------------- BACK ----------------
@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    main_menu(call.message.chat.id, call.message.message_id)

# ---------------- BOTTOM MENU ACTIONS (заготовка) ----------------
@bot.message_handler(commands=['menu'])
def menu(message):
    markup = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("📊 Проверить подписку", callback_data="check")
    btn2 = InlineKeyboardButton("🎥 Пробное видео", callback_data="trial")

    markup.add(btn1)
    markup.add(btn2)

    bot.send_message(message.chat.id, "📱 Меню:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check(call):
    bot.send_message(call.message.chat.id, "⏳ Тут будет проверка подписки")

@bot.callback_query_handler(func=lambda call: call.data == "trial")
def trial(call):
    bot.send_message(call.message.chat.id, "🎥 Тут будет пробное видео")

# ---------------- RUN ----------------
bot.infinity_polling()