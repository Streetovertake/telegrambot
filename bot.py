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

# ---------------- TARIF MENU ----------------
def show_tariffs(chat_id, message_id=None):
    markup = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("🫣 Для неуверенных / HOT", callback_data="tariff_soft")
    btn2 = InlineKeyboardButton("🥵 Для взрослых / PRO", callback_data="tariff_hard")
    menu_btn = InlineKeyboardButton("📱 Меню", callback_data="menu")

    markup.add(btn1)
    markup.add(btn2)
    markup.add(menu_btn)

    text = (
        "👁 <b>Я знаю, зачем ты пришёл…</b>\n"
        "<i>I know why you're here…</i>\n\n"
        "👇 <i>Выбери тариф / Choose your access level</i>"
    )

    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")

# ---------------- HOT ----------------
@bot.callback_query_handler(func=lambda call: call.data == "tariff_soft")
def tariff_soft(call):
    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton("💰 USDT", callback_data="pay_usdt_soft"))
    markup.add(InlineKeyboardButton("💳 Карта банка", callback_data="pay_card_soft"))
    markup.add(InlineKeyboardButton("🚀 Boosty", callback_data="pay_boosty_soft"))
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    text = (
        "🫣 <b>Тариф: HOT</b>\n\n"

        "📌 <i>Описание:</i>\n"
        "• Фотосессии без цензуры\n"
        "• Полные версии материалов\n"
        "• Короткие видео формата TikTok\n"
        "• Доступ в закрытый чат\n"
        "• Регулярное обновление контента\n\n"

        "💰 <b>Цена: 2000₽</b>"
    )

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=markup, parse_mode="HTML")

# ---------------- PRO ----------------
@bot.callback_query_handler(func=lambda call: call.data == "tariff_hard")
def tariff_hard(call):
    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton("💰 USDT", callback_data="pay_usdt_hard"))
    markup.add(InlineKeyboardButton("💳 Карта банка", callback_data="pay_card_hard"))
    markup.add(InlineKeyboardButton("🚀 Boosty", callback_data="pay_boosty_hard"))
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    text = (
        "🥵 <b>Тариф: PRO</b>\n\n"

        "📌 <i>Описание:</i>\n"
        "• Максимальный доступ к контенту\n"
        "• Полная версия всех материалов\n"
        "• Эксклюзивные видео 10–15 минут\n"
        "• Закрытый PRO чат\n"
        "• Возможность кастомных запросов\n\n"

        "💰 <b>Цена: 5000₽</b>"
    )

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=markup, parse_mode="HTML")

# ---------------- USDT PAYMENT ----------------
@bot.callback_query_handler(func=lambda call: "pay_usdt" in call.data)
def pay_usdt(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    text = (
        "💰 <b>Оплата USDT (TRC20)</b>\n\n"
        "📥 <i>Отправь средства на адрес:</i>\n"
        f"<code>{USDT_WALLET}</code>\n\n"
        "⚠️ <i>После оплаты нажми подтверждение</i>"
    )

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=markup, parse_mode="HTML")

# ---------------- CARD ----------------
@bot.callback_query_handler(func=lambda call: "pay_card" in call.data)
def pay_card(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    text = (
        "💳 <b>Оплата картой</b>\n\n"
        "📌 <i>Реквизиты:</i>\n"
        "<code>ВСТАВЬ СЮДА РЕКВИЗИТЫ</code>\n\n"
        "⚠️ <i>После оплаты нажми /paid</i>"
    )

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=markup, parse_mode="HTML")

# ---------------- BOOSTY ----------------
@bot.callback_query_handler(func=lambda call: "pay_boosty" in call.data)
def pay_boosty(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    text = (
        "🚀 <b>Boosty подписка</b>\n\n"
        "📌 <i>Оформи подписку по ссылке:</i>\n"
        "<code>ВСТАВЬ ССЫЛКУ</code>\n\n"
        "⚠️ <i>После оплаты нажми /paid</i>"
    )

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=markup, parse_mode="HTML")

# ---------------- PAID ----------------
@bot.message_handler(commands=['paid'])
def paid(message):
    bot.send_message(message.chat.id,
        "✔ <b>Оплата принята в обработку</b>\n\n"
        "<i>Проверяю вручную. Доступ будет выдан после подтверждения.</i>",
        parse_mode="HTML"
    )

# ---------------- BACK ----------------
@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    show_tariffs(call.message.chat.id, call.message.message_id)

# ---------------- RUN ----------------
bot.infinity_polling()