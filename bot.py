import telebot
import os
from datetime import datetime, timedelta
import threading
import time

ADMIN_ID = 123456789  # <-- поставь свой Telegram ID

CHANNEL_ID = "@your_private_channel"

subs = {}  # user_id: {expire, plan, warned}

PLANS = {
    "basic": {
        "days": 1,
        "price": 600,
        "title": "Basic"
    },
    "middle": {
        "days": 7,
        "price": 1600,
        "title": "Middle"
    },
    "hot": {
        "days": 30,
        "price": 2500,
        "title": "HOT"
    },
    "ahhh": {
        "days": 30,
        "price": 4990,
        "title": "Ahhh..."
    }
}
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)
DEMO_LINK = "https://t.me/+ehe66RnahS5hZTgy"
USDT_WALLET = "ТВОЙ_USDT_АДРЕС"

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    show_tariffs(message.chat.id)
@bot.callback_query_handler(func=lambda call: call.data == "menu")
def menu(call):
    bot.answer_callback_query(call.id)

    try:
        bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
    except:
        pass

    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton("📊 Проверь подписку", callback_data="check"))
    markup.add(InlineKeyboardButton("🔞 FREE РАЗОГРЕВ", callback_data="trial"))
    markup.add(InlineKeyboardButton("🏠 Выбери подписку", callback_data="back"))

    bot.send_message(
        call.message.chat.id,
        "📱 <b>Меню</b>\n\n<i>Выбери действие</i>",
        parse_mode="HTML",
        reply_markup=markup
    )

#--------------------give----------------------
def give_sub(user_id, plan_key):
    plan = PLANS[plan_key]

    subs[user_id] = {
        "expire": datetime.now() + timedelta(days=plan["days"]),
        "plan": plan_key,
        "warned": False
    }

    # уведомление тебе
    bot.send_message(
        ADMIN_ID,
        f"💰 Новая подписка!\n\n"
        f"User: {user_id}\n"
        f"Plan: {plan['title']}\n"
        f"Days: {plan['days']}"
    )

# ---------------- TARIF MENU ----------------
def show_tariffs(chat_id, message_id=None):
    markup = InlineKeyboardMarkup()

    InlineKeyboardButton("💙 Basic 600₽", callback_data="buy_basic")
    InlineKeyboardButton("💛 Middle 1600₽", callback_data="buy_middle")
    InlineKeyboardButton("❤️ HOT 2500₽", callback_data="buy_hot")
    InlineKeyboardButton("🔥 Ahhh 4990₽", callback_data="buy_ahhh")
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
        
#-----------------TRIAL----------------
@bot.callback_query_handler(func=lambda call: call.data == "trial")
def trial(call):
    bot.answer_callback_query(call.id)

    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(
            "🎥 🔞 Надень наушники",
            url=DEMO_LINK
        )
    )

    markup.add(
        InlineKeyboardButton(
            "⬅ Назад",
            callback_data="back"
        )
    )

    bot.edit_message_text(
        "🎥 <b>Разогрев / Warmup</b>\n\n"
        "<i>🔞👇Нажми внизу и насладись 👇🔞</i>",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
        reply_markup=markup
    )

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
    @bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
    
def buy(call):
    user_id = call.from_user.id
    plan = call.data.replace("buy_", "")

    give_sub(user_id, plan)

    bot.send_message(
        user_id,
        f"✔ {PLANS[plan]['title']} активирован 🔥"
    )

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

#------------------check----------------
def check_subs():
    while True:
        now = datetime.now()

        for user_id in list(subs.keys()):
            data = subs[user_id]

            # ❌ истёк срок → удаляем
            if data["expire"] < now:
                try:
                    bot.kick_chat_member(CHANNEL_ID, user_id)
                    bot.unban_chat_member(CHANNEL_ID, user_id)
                except:
                    pass

                del subs[user_id]
                continue

            # ⚠️ предупреждение за 24 часа
            if not data["warned"]:
                if (data["expire"] - now).total_seconds() < 86400:
                    try:
                        bot.send_message(
                            user_id,
                            "⚠️ Подписка скоро закончится!"
                        )
                        data["warned"] = True
                    except:
                        pass

        time.sleep(60)

# ---------------- BACK ----------------
@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    bot.answer_callback_query(call.id)

    try:
        bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
    except:
        pass

    show_tariffs(call.message.chat.id)
    
# ---------------- RUN ----------------
bot.infinity_polling()