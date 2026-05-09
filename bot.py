import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)
trial = "BAACAgIAAxkBAAPCaf9DaCB7kwuocGIH8zyWNb9hpqoAAruWAAJEdPhLDN9OG5h42Kk7BA"
USDT_WALLET = "ТВОЙ_USDT_АДРЕС"

# ---------------- START ----------------
@bot.callback_query_handler(func=lambda call: call.data == "menu")
def menu(call):
    bot.answer_callback_query(call.id)

    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton("📊 Проверить подписку", callback_data="check"))
    markup.add(InlineKeyboardButton("🎥 Пробное видео", callback_data="trial"))
    markup.add(InlineKeyboardButton("🏠 Тарифы", callback_data="back"))

    bot.edit_message_text(
        "📱 <b>Меню</b>\n\n<i>Выбери действие</i>",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode="HTML"
    )
#----------------------------------------
@bot.callback_query_handler(func=lambda call: call.data == "trial")
def trial(call):
    bot.answer_callback_query(call.id)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 Назад", callback_data="menu"))

    bot.send_message(
        call.message.chat.id,
        "🎥 <i>Пробное видео</i>\n\n<i>Демо-контент</i>",
        parse_mode="HTML",
        reply_markup=markup
    )

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
        "🌭 <b>Я знаю, зачем ты пришёл…</b> 🌭\n"
        "🌭 <i>I know why you're here…</i> 🌭\n\n"
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
        " 🌭 Фотосессии без цензуры! (Ну всё видно ой-ой-ой)\n\n"
        " 🌭 Короткие видео вертикального формата! (Тиктоковые/Инстаграмовые)\n\n"
        " 🌭 Доступ в закрытый HOT чат! (я там с вами болтать буду)\n\n"
        " 🌭 Небольшие взрослые видео (соло)\n\n"
        " 🌭 Регулярное обновление контента\n\n"

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
        " 🔞 Максимальный доступ ко всему контенту.🥵\n\n"
        " 🔞 Большие взрослые игрушки, и даже ДВЕ иногда.\n\n"
        " 🔞 Мокрые окончания, Кримпай, Крики; Попность, Оральность и вообще все что можно. 🫣\n\n"
        " 🔞 Эксклюзивные видео даже 10 и даже 15 минут, представь себе?\n\n"
        " 🔞 Доступ в закрытый PRO чат (я там постоянно)\n\n"
        " 🔞 Возможность заказать кастомный Кружок/Видео/Сигну.\n\n"

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
        "<i>Я лично сама проверяю денюжки. Если долго не добавляю, не злись зайка, скоро добавлю.</i>",
        parse_mode="HTML"
    )

# ---------------- BACK ----------------
@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    show_tariffs(call.message.chat.id, call.message.message_id)

@bot.message_handler(content_types=['video'])
def get_video(message):
    print(message.video.file_id)
    bot.send_message(message.chat.id, message.video.file_id)
    
# ---------------- RUN ----------------
bot.infinity_polling()