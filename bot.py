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
    markup.add(InlineKeyboardButton("📊 Проверь подписку", callback_data="check"))
    markup.add(InlineKeyboardButton("🔞 Разогрейся бесплатно", callback_data="trial"))
    markup.add(InlineKeyboardButton("🏠 Выбери подписку", callback_data="back"))

    bot.send_message(
        call.message.chat.id,
        "📱 <b>Меню</b>",
        parse_mode="HTML",
        reply_markup=markup
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

    markup.add(InlineKeyboardButton("💙 Basic 1D", callback_data="buy_basic"))
    markup.add(InlineKeyboardButton("💛 Middle 1W", callback_data="buy_middle"))
    markup.add(InlineKeyboardButton("❤️ HOT 1M", callback_data="buy_hot"))
    markup.add(InlineKeyboardButton("🔥 Ahhh... V.I.P.", callback_data="buy_ahhh"))
    markup.add(InlineKeyboardButton("📱 Меню", callback_data="menu"))

    text = "🌭 <b>Привет, зайчик, это мой бот для выдачи доступа к моим приваточкам!</b>\n<b>Hi sweetie, this is my private access bot</b>\n👇<i>Выбери подходящий тариф / Choose a plan</i>👇"

    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")

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
    markup.add(InlineKeyboardButton("🔞 Надень наушники 🔞", url=DEMO_LINK))
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    bot.edit_message_text(
        "🎥 <b>Разогрев</b>",
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
    bot.edit_message_text(
        "💳 Карта:\n<code>реквизиты</code>",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML"
    )

# ---------------- BOOSTY ----------------
@bot.callback_query_handler(func=lambda call: "pay_boosty" in call.data)
def pay_boosty(call):
    bot.edit_message_text(
        "🚀 Boosty:\n<code>ссылка</code>",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML"
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
    show_tariffs(call.message.chat.id)
    
@bot.message_handler(content_types=['text'])
def test(message):
    print(message.chat.id)

# ---------------- RUN ----------------
threading.Thread(target=check_subs, daemon=True).start()
bot.infinity_polling()
pyTelegramBotAPI
python-dotenv