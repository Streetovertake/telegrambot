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
# ---------------- BOT INIT ----------------
bot = telebot.TeleBot(TOKEN)

# ---------------- STORAGE ----------------
subs = {}  # user_id: {expire, plan, warned}

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

    markup.add(
        InlineKeyboardButton(
            "📊 ПРОВЕРКА ПОДПИСКИ",
            callback_data="check"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "🔞 БЕСПЛАТНЫЙ РАЗОГРЕВ",
            callback_data="trial"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "🏠 ВАРИАНТЫ ПОДПИСОК:3",
            callback_data="back"
        )
    )

    bot.edit_message_text(
        "📱 <b>МЕНЮ НАВИГАЦИИ В БОТЕ</b>\n\n"
        "<i>Выбери нужный раздел</i>",

        call.message.chat.id,
        call.message.message_id,

        parse_mode="HTML",
        reply_markup=markup
    )

#-------------------plan oplata---------------
def show_plan(call, title, desc, price, plan_key):
    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton("💰 USDT", callback_data=f"pay_usdt_{plan_key}")
    )
    markup.add(
        InlineKeyboardButton("💳 Карта", callback_data=f"pay_card_{plan_key}")
    )
    markup.add(
        InlineKeyboardButton("🚀 Boosty", callback_data=f"pay_boosty_{plan_key}")
    )
    markup.add(
        InlineKeyboardButton("⬅ Назад", callback_data="back")
    )

    text = (
        f"🔥 <b>{title}</b>\n\n"
        f"{desc}\n\n"
        f"💰 <b>Цена: {price}₽</b>\n\n"
        f"👇 <i>Выбери способ оплаты</i>"
    )

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
        reply_markup=markup
    )
    
#-------------------show-plan-----------------
def show_plan(call, title, desc, price, plan_key):

    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(
            "💳 Карта",
            callback_data=f"pay_card_{plan_key}"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "🚀 Boosty",
            callback_data=f"pay_boosty_{plan_key}"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "💰 USDT",
            callback_data=f"pay_usdt_{plan_key}"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "⬅ Назад",
            callback_data="back"
        )
    )

    text = (
        f"🔥 <b>{title}</b>\n\n"
        f"{desc}\n\n"
        f"💸 <b>Цена: {price}₽</b>\n\n"
        f"<i>Выбери способ оплаты:</i>"
    )

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
        reply_markup=markup
    )
# ------------------basic---------------------
@bot.callback_query_handler(func=lambda call: call.data == "buy_basic")
def buy_basic(call):

    show_plan(
        call,
        "Basic / 1 день",
        "❤️ <i>Доступ на 24 часа в сладенький контент из подписки HOT</i>❤️\n\n"
        "❤️ <i>Красивые фотосессии в сочных косплеях</i>!\n\n"
        "❤️ <i>Короткие вертикальные видео БЕЗ ЦЕНЗУРЫ</i>\n\n"
        "😔 <i>Минусы: Без доступа к чатику</i>",

        600,
        "basic"
    )
    
# ------------------middle--------------------
@bot.callback_query_handler(func=lambda call: call.data == "buy_middle")
def buy_middle(call):

    show_plan(
        call,
        "Middle / 1 неделя",
        "❤️ <i>Доступ на <b>7 дней</b> в сладенький контент из подписки HOT</i>❤️\n\n"
        "❤️ <i>Красивые фотосессии в сочных косплеях</i>!\n\n"
        "❤️ <i>Короткие вертикальные видео БЕЗ ЦЕНЗУРЫ</i>\n\n"
        "😔 <i>Минусы: Без доступа к чатику</i>",

        1600,
        "middle"
    )
# -------------------HOT---------------------
@bot.callback_query_handler(func=lambda call: call.data == "buy_hot")
def buy_hot(call):

    show_plan(
        call,
        "HOT / 1 месяц",
        "❤️ <i>Доступ на <b>30 дней</b> в сладенький контент из подписки HOT</i>❤️\n\n"
        "❤️ <i>Красивые фотосессии в сочных косплеях</i>!\n\n"
        "❤️ <i>Короткие вертикальные видео БЕЗ ЦЕНЗУРЫ</i>\n\n"
        "❤️ +Доступ в горяченный чат, в котором я общаюсь с вами!(<i>Псс... я даже кружочки скидываю туда</i>)",

        2500,
        "hot"
    )
#-------------------Ass-----------------------
@bot.callback_query_handler(func=lambda call: call.data == "buy_ahhh")
def buy_ahhh(call):

    show_plan(
        call,
        "Ahhh... VIP",
        "🥵<b>Доступ к САМОМУ ГОРЯЧЕННОМУ И САМОМУ ВЗРОСЛОМУ КОНТЕНТУ🥵</b>\n\n"
        "🔞Мои соло-игры, поповые, ротовые и всякие ваши фантазийные тут есть\n\n"
        "🔞Регулярное пополнение контентом (От 2 раз в неделю)\n\n"
        "🔞Мои стоны, Кримпай, Крики и Слезы БЕЗ ЦЕНЗУРЫ!\n\n"
        "🔞Длинные видео по 10-15 минуток!\n\n"
        "🔞Возможность заказать кастомные видео/кружки/сигнушки!\n\n"
        "🔞+Доступ к V.I.P чату, в котором общаюсь всегда!\n\n",

        4990,
        "ahhh"
    )
# ---------------- GIVE SUB ----------------
def give_sub(user_id, plan_key):
    plan = PLANS[plan_key]

    subs[user_id] = {
        "expire": datetime.now() + timedelta(days=plan["days"]),
        "plan": plan_key,
        "warned": False
    }

    bot.send_message(
        ADMIN_ID,
        f"💰 НОВАЯ ОПЛАТА\nUser: {user_id}\nPlan: {plan['title']}"
    )

# ---------------- TARIFS ----------------
def show_tariffs(chat_id, message_id=None):
    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton("💙 Basic / 1 DAY", callback_data="buy_basic"))
    markup.add(InlineKeyboardButton("💛 Middle / 1 WEEK", callback_data="buy_middle"))
    markup.add(InlineKeyboardButton("❤️ HOT / 1 MONTH", callback_data="buy_hot"))
    markup.add(InlineKeyboardButton("🔥 Ahhh... V.I.P. / 1 MONTH", callback_data="buy_ahhh"))
    markup.add(InlineKeyboardButton("📱 Меню", callback_data="menu"))

    text = "🌭 <b>Привет, зайчик...</b>"

    try:
        bot.edit_message_text(
            text,
            chat_id,
            message_id,
            reply_markup=markup,
            parse_mode="HTML"
        )
    except:
        bot.send_message(
            chat_id,
            text,
            reply_markup=markup,
            parse_mode="HTML"
        )
# ---------------- BUY ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy(call):
    user_id = call.from_user.id
    plan = call.data.replace("buy_", "")

    give_sub(user_id, plan)

    bot.send_message(user_id, f"✔ {PLANS[plan]['title']} активирован 🔥")

# ---------------- TRIAL ----------------
@bot.callback_query_handler(func=lambda call: call.data == "trial")
def trial(call):
    bot.answer_callback_query(call.id)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔞 Надень наушники / Use your headphones 🔞", url=DEMO_LINK))
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    bot.edit_message_text(
        "🎥 <b>ПРОБНОЕ ВИДЕО 🔞\n ПОСМОТРИ, ЧТОБЫ СКОРЕЕ РЕШИТЬСЯ НА ПОДПИСКУ / CHECK TRIAL VIDEO</b>",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode="HTML"
    )

# ---------------- USDT ----------------
@bot.callback_query_handler(func=lambda call: "pay_usdt" in call.data)
def pay_usdt(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    bot.edit_message_text(
        f"💰 USDT:\n<code>{USDT_WALLET}</code>",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode="HTML"
    )

# ---------------- CARD ----------------
@bot.callback_query_handler(func=lambda call: "pay_card" in call.data)
def pay_card(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    bot.edit_message_text(
        "💳 Ты выбрал оплату картой\n\n После перевода скидывай скриншот сюда и жди, я пока все проверю:\n\n <code>Номер карты: 2202228406930000</code>",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
        reply_markup=markup
    )

# ---------------- BOOSTY ----------------
@bot.callback_query_handler(func=lambda call: "pay_boosty" in call.data)
def pay_boosty(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    bot.edit_message_text(
        "🚀 Ты выбрал оплату через подписку BOOSTY\n <i> Все просто, переходишь по ссылочке на бусти, оплачиваешь любым удобным способом (СБП, Переводом и т.д.), скидываешь скриншот и никнейм на бусти, я пока все проверю и выдам доступ!</i>:\n<code>Ссылка на бусти</code>",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
        reply_markup=markup
    )

# ---------------- CHECK SUBS ----------------
def check_subs():
    while True:
        now = datetime.now()

        for user_id in list(subs.keys()):
            data = subs[user_id]

            if data["expire"] < now:
                try:
                    bot.kick_chat_member(CHANNEL_ID, user_id)
                    bot.unban_chat_member(CHANNEL_ID, user_id)
                except:
                    pass

                del subs[user_id]
                continue

            if not data["warned"]:
                if (data["expire"] - now).total_seconds() < 86400:
                    try:
                        bot.send_message(user_id, "⚠️ Подписка заканчивается")
                        data["warned"] = True
                    except:
                        pass

        time.sleep(60)

# ---------------- BACK ----------------
@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    bot.answer_callback_query(call.id)

    show_tariffs(
        call.message.chat.id,
        call.message.message_id
    )

# ---------------- RUN ----------------
threading.Thread(target=check_subs, daemon=True).start()
bot.infinity_polling()
pyTelegramBotAPI
python-dotenv