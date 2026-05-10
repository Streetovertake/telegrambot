
cat > /mnt/user-data/outputs/bot.py << 'ENDOFFILE'
import telebot
import os
import threading
import time
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ - zadaj ih v hostinge:
#
# TOKEN              - token bota ot @BotFather
# ADMIN_ID           - tvoj Telegram ID (chislo, uznat u @userinfobot)
# ADMIN_USERNAME     - tvoj username bez @ (primer: myusername)
# CARD_NUMBER        - nomer karty
# USDT_WALLET        - adres USDT koshelka
# BOOSTY_URL         - https://boosty.to/...
# TRIAL_CHANNEL_URL  - https://t.me/+...
# CHANNEL_ID         - ID zakrytogo kanala 1-3 urovnej (chislo so znakom minus)
# CHAT_ID            - ID obychnogo chata 3 uroven (chislo so znakom minus)
# VIP_CHANNEL_ID     - ID VIP kanala 4 uroven (chislo so znakom minus)
# VIP_CHAT_ID        - ID VIP chata 4 uroven (chislo so znakom minus)
# TIKTOK_URL         - https://tiktok.com/@...
# INSTAGRAM_URL      - https://instagram.com/...
# MAIN_CHANNEL_URL   - https://t.me/...

TOKEN             = os.environ["TOKEN"]
ADMIN_ID          = int(os.environ["ADMIN_ID"])
ADMIN_USERNAME    = os.environ.get("ADMIN_USERNAME", "admin")
CARD_NUMBER       = os.environ.get("CARD_NUMBER", "0000 0000 0000 0000")
USDT_WALLET       = os.environ.get("USDT_WALLET", "wallet_address")
BOOSTY_URL        = os.environ.get("BOOSTY_URL", "https://boosty.to/")
TRIAL_CHANNEL_URL = os.environ.get("TRIAL_CHANNEL_URL", "https://t.me/")
CHANNEL_ID        = int(os.environ["CHANNEL_ID"])
CHAT_ID           = int(os.environ["CHAT_ID"])
VIP_CHANNEL_ID    = int(os.environ["VIP_CHANNEL_ID"])
VIP_CHAT_ID       = int(os.environ["VIP_CHAT_ID"])
TIKTOK_URL        = os.environ.get("TIKTOK_URL", "https://tiktok.com/")
INSTAGRAM_URL     = os.environ.get("INSTAGRAM_URL", "https://instagram.com/")
MAIN_CHANNEL_URL  = os.environ.get("MAIN_CHANNEL_URL", "https://t.me/")

bot = telebot.TeleBot(TOKEN)

subs             = {}
pending_payments = {}
user_state       = {}

PLANS = {
    "lvl1": {
        "days": 1, "price": 600, "title": "1 uroveny",
        "duration": "1 den", "vip": False,
        "description": (
            "1\u20e3 <b>1 \u0443\u0440\u043e\u0432\u0435\u043d\u044c \u2014 600\u20bd / 1 \u0434\u0435\u043d\u044c</b>\n\n"
            "\u2705 \u0414\u043e\u0441\u0442\u0443\u043f \u043a \u0437\u0430\u043a\u0440\u044b\u0442\u043e\u043c\u0443 \u043a\u0430\u043d\u0430\u043b\u0443\n"
            "\u2705 \u0412\u0435\u0441\u044c \u043a\u043e\u043d\u0442\u0435\u043d\u0442 \u0437\u0430 \u0434\u0435\u043d\u044c\n\n"
            "\u0418\u0434\u0435\u0430\u043b\u044c\u043d\u043e \u0447\u0442\u043e\u0431\u044b \u043f\u043e\u0437\u043d\u0430\u043a\u043e\u043c\u0438\u0442\u044c\u0441\u044f \u0441 \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u043e\u043c."
        ),
    },
    "lvl2": {
        "days": 7, "price": 1590, "title": "2 uroveny",
        "duration": "1 nedelya", "vip": False,
        "description": (
            "2\u20e3 <b>2 \u0443\u0440\u043e\u0432\u0435\u043d\u044c \u2014 1590\u20bd / 1 \u043d\u0435\u0434\u0435\u043b\u044f</b>\n\n"
            "\u2705 \u0414\u043e\u0441\u0442\u0443\u043f \u043a \u0437\u0430\u043a\u0440\u044b\u0442\u043e\u043c\u0443 \u043a\u0430\u043d\u0430\u043b\u0443\n"
            "\u2705 \u0412\u0435\u0441\u044c \u043a\u043e\u043d\u0442\u0435\u043d\u0442 \u0437\u0430 \u043d\u0435\u0434\u0435\u043b\u044e\n\n"
            "\u041e\u0442\u043b\u0438\u0447\u043d\u044b\u0439 \u0441\u0442\u0430\u0440\u0442 \u0434\u043b\u044f \u043f\u043e\u0433\u0440\u0443\u0436\u0435\u043d\u0438\u044f."
        ),
    },
    "lvl3": {
        "days": 30, "price": 2690, "title": "3 uroveny",
        "duration": "1 mesyac", "vip": False,
        "description": (
            "3\u20e3 <b>3 \u0443\u0440\u043e\u0432\u0435\u043d\u044c \u2014 2690\u20bd / 1 \u043c\u0435\u0441\u044f\u0446</b>\n\n"
            "\u2705 \u0414\u043e\u0441\u0442\u0443\u043f \u043a \u0437\u0430\u043a\u0440\u044b\u0442\u043e\u043c\u0443 \u043a\u0430\u043d\u0430\u043b\u0443\n"
            "\u2705 \u0414\u043e\u0441\u0442\u0443\u043f \u043a \u0437\u0430\u043a\u0440\u044b\u0442\u043e\u043c\u0443 \u0447\u0430\u0442\u0443\n"
            "\u2705 \u0412\u0435\u0441\u044c \u043a\u043e\u043d\u0442\u0435\u043d\u0442 \u0437\u0430 \u043c\u0435\u0441\u044f\u0446\n\n"
            "\u041c\u0430\u043a\u0441\u0438\u043c\u0443\u043c \u043f\u043e\u043b\u044c\u0437\u044b \u043d\u0430 \u043c\u0435\u0441\u044f\u0446 \u0432\u043f\u0435\u0440\u0451\u0434."
        ),
    },
    "lvl4": {
        "days": 30, "price": 4990, "title": "4 uroveny (VIP)",
        "duration": "1 mesyac", "vip": True,
        "description": (
            "\U0001f451 <b>4 \u0443\u0440\u043e\u0432\u0435\u043d\u044c VIP \u2014 4990\u20bd / 1 \u043c\u0435\u0441\u044f\u0446</b>\n\n"
            "\u2705 \u0414\u043e\u0441\u0442\u0443\u043f \u043a VIP \u043a\u0430\u043d\u0430\u043b\u0443\n"
            "\u2705 \u0414\u043e\u0441\u0442\u0443\u043f \u043a VIP \u0447\u0430\u0442\u0443\n"
            "\u2705 \u042d\u043a\u0441\u043a\u043b\u044e\u0437\u0438\u0432\u043d\u044b\u0439 \u043a\u043e\u043d\u0442\u0435\u043d\u0442\n\n"
            "\u26a0\ufe0f <b>\u0412\u043d\u0438\u043c\u0430\u043d\u0438\u0435:</b> \u043f\u0440\u0438 \u043f\u043e\u043a\u0443\u043f\u043a\u0435 VIP \u0432\u0441\u0435 \u043f\u0440\u0435\u0434\u044b\u0434\u0443\u0449\u0438\u0435 "
            "\u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0438 \u0430\u043d\u043d\u0443\u043b\u0438\u0440\u0443\u044e\u0442\u0441\u044f \u0438 \u0437\u0430\u043c\u0435\u043d\u044f\u044e\u0442\u0441\u044f \u043d\u0430 VIP \u043d\u0430 1 \u043c\u0435\u0441\u044f\u0446."
        ),
    },
}


def answer(call, text=""):
    try:
        bot.answer_callback_query(call.id, text)
    except Exception:
        pass


def safe_edit(call, text, markup=None):
    try:
        bot.edit_message_text(
            text, call.message.chat.id, call.message.message_id,
            reply_markup=markup, parse_mode="HTML",
        )
    except Exception as e:
        print("safe_edit:", e)


def menu_btn():
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("\u2b05 \u041d\u0430\u0437\u0430\u0434 \u0432 \u043c\u0435\u043d\u044e", callback_data="menu"))
    return m


def add_user_to_channels(uid, plan_key):
    plan = PLANS[plan_key]
    invite_channel = None
    invite_chat = None
    try:
        if plan["vip"]:
            lnk = bot.create_chat_invite_link(VIP_CHANNEL_ID, member_limit=1)
            invite_channel = lnk.invite_link
            lnk2 = bot.create_chat_invite_link(VIP_CHAT_ID, member_limit=1)
            invite_chat = lnk2.invite_link
        else:
            lnk = bot.create_chat_invite_link(CHANNEL_ID, member_limit=1)
            invite_channel = lnk.invite_link
            if plan_key == "lvl3":
                lnk2 = bot.create_chat_invite_link(CHAT_ID, member_limit=1)
                invite_chat = lnk2.invite_link
    except Exception as e:
        print("create invite link error:", e)
    return invite_channel, invite_chat


def kick_user_from_channels(uid, plan_key):
    plan = PLANS[plan_key]
    targets = [VIP_CHANNEL_ID, VIP_CHAT_ID] if plan["vip"] else [CHANNEL_ID]
    if not plan["vip"] and plan_key == "lvl3":
        targets.append(CHAT_ID)
    for chat in targets:
        try:
            bot.ban_chat_member(chat, uid)
            bot.unban_chat_member(chat, uid)
        except Exception as e:
            print("kick error:", e)


def show_menu(chat_id, message_id=None):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("\U0001f4b0 \u0421\u043f\u0438\u0441\u043e\u043a \u0442\u0430\u0440\u0438\u0444\u043e\u0432", callback_data="tariffs"))
    markup.add(InlineKeyboardButton("\U0001f3a5 \u041f\u0440\u043e\u0431\u043d\u043e\u0435 \u0432\u0438\u0434\u0435\u043e", callback_data="trial"))
    markup.add(InlineKeyboardButton("\U0001f4ca \u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0438", callback_data="check"))
    markup.add(InlineKeyboardButton("\U0001f517 \u0421\u0441\u044b\u043b\u043a\u0438 \u043d\u0430 \u043c\u0435\u043d\u044f", callback_data="links"))
    text = (
        "\U0001f44b <b>\u0414\u043e\u0431\u0440\u043e \u043f\u043e\u0436\u0430\u043b\u043e\u0432\u0430\u0442\u044c!</b>\n\n"
        "\u0417\u0434\u0435\u0441\u044c \u0442\u044b \u043c\u043e\u0436\u0435\u0448\u044c \u043e\u0444\u043e\u0440\u043c\u0438\u0442\u044c \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0443, "
        "\u043f\u043e\u0441\u043c\u043e\u0442\u0440\u0435\u0442\u044c \u043f\u0440\u043e\u0431\u043d\u043e\u0435 \u0432\u0438\u0434\u0435\u043e "
        "\u0438\u043b\u0438 \u043f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c \u0441\u0442\u0430\u0442\u0443\u0441 \u0441\u0432\u043e\u0435\u0439 \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0438.\n\n"
        "\u0412\u044b\u0431\u0435\u0440\u0438 \u043d\u0443\u0436\u043d\u044b\u0439 \u0440\u0430\u0437\u0434\u0435\u043b:"
    )
    if message_id:
        try:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
            return
        except Exception:
            pass
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


@bot.message_handler(commands=["start"])
def cmd_start(message):
    show_menu(message.chat.id)


@bot.callback_query_handler(func=lambda c: c.data == "menu")
def cb_menu(call):
    answer(call)
    show_menu(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda c: c.data == "links")
def cb_links(call):
    answer(call)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("\U0001f3b5 TikTok", url=TIKTOK_URL))
    markup.add(InlineKeyboardButton("\U0001f4f8 Instagram", url=INSTAGRAM_URL))
    markup.add(InlineKeyboardButton("\U0001f680 Boosty", url=BOOSTY_URL))
    markup.add(InlineKeyboardButton("\U0001f4e2 \u041e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u043a\u0430\u043d\u0430\u043b", url=MAIN_CHANNEL_URL))
    markup.add(InlineKeyboardButton("\U0001f4ac \u0421\u0432\u044f\u0437\u044c \u0441\u043e \u043c\u043d\u043e\u0439", url="https://t.me/" + ADMIN_USERNAME))
    markup.add(InlineKeyboardButton("\u2b05 \u041d\u0430\u0437\u0430\u0434", callback_data="menu"))
    safe_edit(call, "\U0001f517 <b>\u041c\u043e\u0438 \u0441\u0441\u044b\u043b\u043a\u0438</b>\n\n\u0412\u044b\u0431\u0435\u0440\u0438 \u043a\u0443\u0434\u0430 \u043f\u0435\u0440\u0435\u0439\u0442\u0438:", markup)


@bot.callback_query_handler(func=lambda c: c.data == "trial")
def cb_trial(call):
    answer(call)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("\U0001f3a7 \u041d\u0430\u0434\u0435\u043d\u044c \u043d\u0430\u0443\u0448\u043d\u0438\u043a\u0438", url=TRIAL_CHANNEL_URL))
    markup.add(InlineKeyboardButton("\u2b05 \u041d\u0430\u0437\u0430\u0434", callback_data="menu"))
    safe_edit(
        call,
        "\U0001f3a5 <b>\u041f\u0440\u043e\u0431\u043d\u043e\u0435 \u0432\u0438\u0434\u0435\u043e</b>\n\n"
        "\u041d\u0430\u0434\u0435\u043d\u044c \u043d\u0430\u0443\u0448\u043d\u0438\u043a\u0438 \u0438 \u043d\u0430\u0436\u043c\u0438 \u043a\u043d\u043e\u043f\u043a\u0443 \u043d\u0438\u0436\u0435 \u2014 "
        "\u0442\u0435\u0431\u044f \u043f\u0435\u0440\u0435\u043d\u0435\u0441\u0451\u0442 \u0432 \u043a\u0430\u043d\u0430\u043b \u0441 \u043f\u0440\u043e\u0431\u043d\u044b\u043c \u0432\u0438\u0434\u0435\u043e.\n\n"
        "\u23f3 \u0414\u043e\u0441\u0442\u0443\u043f \u043e\u0442\u043a\u0440\u044b\u0442 \u043d\u0430 <b>24 \u0447\u0430\u0441\u0430</b>.",
        markup,
    )


@bot.callback_query_handler(func=lambda c: c.data == "check")
def cb_check(call):
    answer(call)
    uid = call.from_user.id
    sub = subs.get(uid)
    if not sub or (sub["expire"] - datetime.now()).total_seconds() <= 0:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("\U0001f4b0 \u041a\u0443\u043f\u0438\u0442\u044c \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0443", callback_data="tariffs"))
        markup.add(InlineKeyboardButton("\u2b05 \u041d\u0430\u0437\u0430\u0434", callback_data="menu"))
        safe_edit(call, "\u274c <b>\u041d\u0435\u0442 \u0430\u043a\u0442\u0438\u0432\u043d\u044b\u0445 \u043f\u043e\u0434\u043f\u0438\u0441\u043e\u043a</b>\n\n\u041e\u0444\u043e\u0440\u043c\u0438 \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0443 \u0447\u0442\u043e\u0431\u044b \u043f\u043e\u043b\u0443\u0447\u0438\u0442\u044c \u0434\u043e\u0441\u0442\u0443\u043f.", markup)
        return
    remaining = sub["expire"] - datetime.now()
    days = remaining.days
    hours = remaining.seconds // 3600
    p = PLANS[sub["plan"]]
    safe_edit(
        call,
        "\u2705 <b>\u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0430 \u0430\u043a\u0442\u0438\u0432\u043d\u0430</b>\n\n"
        "\U0001f4e6 \u0422\u0430\u0440\u0438\u0444: " + p["title"] + "\n"
        "\u23f3 \u041e\u0441\u0442\u0430\u043b\u043e\u0441\u044c: " + str(days) + " \u0434\u043d. " + str(hours) + " \u0447.\n"
        "\U0001f4c5 \u0414\u043e: " + sub["expire"].strftime("%d.%m.%Y %H:%M"),
        menu_btn(),
    )


@bot.callback_query_handler(func=lambda c: c.data == "tariffs")
def cb_tariffs(call):
    answer(call)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("1\u20e3  600\u20bd  \u2014 1 \u0434\u0435\u043d\u044c", callback_data="plan_lvl1"))
    markup.add(InlineKeyboardButton("2\u20e3  1590\u20bd \u2014 1 \u043d\u0435\u0434\u0435\u043b\u044f", callback_data="plan_lvl2"))
    markup.add(InlineKeyboardButton("3\u20e3  2690\u20bd \u2014 1 \u043c\u0435\u0441\u044f\u0446", callback_data="plan_lvl3"))
    markup.add(InlineKeyboardButton("\U0001f451  4990\u20bd \u2014 VIP \u043c\u0435\u0441\u044f\u0446", callback_data="plan_lvl4"))
    markup.add(InlineKeyboardButton("\u2b05 \u041d\u0430\u0437\u0430\u0434", callback_data="menu"))
    safe_edit(call, "\U0001f4b0 <b>\u0412\u044b\u0431\u0435\u0440\u0438 \u0442\u0430\u0440\u0438\u0444</b>\n\n\u041d\u0430\u0436\u043c\u0438 \u043d\u0430 \u0442\u0430\u0440\u0438\u0444 \u0447\u0442\u043e\u0431\u044b \u0443\u0432\u0438\u0434\u0435\u0442\u044c \u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435:", markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith("plan_"))
def cb_plan(call):
    answer(call)
    uid = call.from_user.id
    key = call.data[5:]
    if key not in PLANS:
        return
    user_state[uid] = {"plan": key, "method": None, "receipt_file_id": None}
    p = PLANS[key]
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("\U0001f680 Boosty", callback_data="method_boosty_" + key))
    markup.add(InlineKeyboardButton("\U0001f4b3 \u041a\u0430\u0440\u0442\u0430", callback_data="method_card_" + key))
    markup.add(InlineKeyboardButton("\U0001f4b0 USDT", callback_data="method_usdt_" + key))
    markup.add(InlineKeyboardButton("\u2b05 \u041d\u0430\u0437\u0430\u0434", callback_data="tariffs"))
    safe_edit(call, p["description"] + "\n\n\U0001f4b3 <b>\u0412\u044b\u0431\u0435\u0440\u0438 \u0441\u043f\u043e\u0441\u043e\u0431 \u043e\u043f\u043b\u0430\u0442\u044b:</b>", markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith("method_"))
def cb_method(call):
    answer(call)
    uid = call.from_user.id
    if uid in pending_payments:
        answer(call, "\u26a0\ufe0f \u0423 \u0442\u0435\u0431\u044f \u0443\u0436\u0435 \u0435\u0441\u0442\u044c \u0430\u043a\u0442\u0438\u0432\u043d\u0430\u044f \u0437\u0430\u044f\u0432\u043a\u0430, \u043e\u0436\u0438\u0434\u0430\u0439 \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u044f")
        return
    parts = call.data.split("_")
    method = parts[1]
    key = parts[2]
    if key not in PLANS:
        return
    user_state[uid] = {"plan": key, "method": method, "receipt_file_id": None}
    p = PLANS[key]
    markup = InlineKeyboardMarkup()
    if method == "boosty":
        markup.add(InlineKeyboardButton("\U0001f4b3 \u041f\u0435\u0440\u0435\u0439\u0442\u0438 \u043a \u043e\u043f\u043b\u0430\u0442\u0435", url=BOOSTY_URL))
        markup.add(InlineKeyboardButton("\u2705 \u042f \u043e\u043f\u043b\u0430\u0442\u0438\u043b", callback_data="paid"))
        markup.add(InlineKeyboardButton("\u2b05 \u041d\u0430\u0437\u0430\u0434", callback_data="plan_" + key))
        text = (
            "\U0001f680 <b>\u041e\u043f\u043b\u0430\u0442\u0430 \u0447\u0435\u0440\u0435\u0437 Boosty</b>\n\n"
            "\U0001f4e6 \u0422\u0430\u0440\u0438\u0444: " + p["title"] + " \u2014 " + str(p["price"]) + "\u20bd\n\n"
            "1. \u041d\u0430\u0436\u043c\u0438 <b>\u00ab\u041f\u0435\u0440\u0435\u0439\u0442\u0438 \u043a \u043e\u043f\u043b\u0430\u0442\u0435\u00bb</b>\n"
            "2. \u041e\u0444\u043e\u0440\u043c\u0438 \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0443 \u043d\u0430 Boosty\n"
            "3. \u0421\u0434\u0435\u043b\u0430\u0439 \u0441\u043a\u0440\u0438\u043d\u0448\u043e\u0442 \u0447\u0435\u043a\u0430\n"
            "4. \u041e\u0442\u043f\u0440\u0430\u0432\u044c \u0441\u043a\u0440\u0438\u043d\u0448\u043e\u0442 \u0441\u044e\u0434\u0430 \u0432 \u0447\u0430\u0442\n"
            "5. \u041d\u0430\u0436\u043c\u0438 <b>\u00ab\u042f \u043e\u043f\u043b\u0430\u0442\u0438\u043b\u00bb</b>"
        )
    elif method == "card":
        markup.add(InlineKeyboardButton("\u2705 \u042f \u043e\u043f\u043b\u0430\u0442\u0438\u043b", callback_data="paid"))
        markup.add(InlineKeyboardButton("\u2b05 \u041d\u0430\u0437\u0430\u0434", callback_data="plan_" + key))
        text = (
            "\U0001f4b3 <b>\u041e\u043f\u043b\u0430\u0442\u0430 \u043a\u0430\u0440\u0442\u043e\u0439</b>\n\n"
            "\U0001f4e6 \u0422\u0430\u0440\u0438\u0444: " + p["title"] + " \u2014 " + str(p["price"]) + "\u20bd\n\n"
            "\u041f\u0435\u0440\u0435\u0432\u0435\u0434\u0438 <b>" + str(p["price"]) + "\u20bd</b> \u043d\u0430 \u043a\u0430\u0440\u0442\u0443:\n\n"
            "<code>" + CARD_NUMBER + "</code>\n\n"
            "1. \u041f\u0435\u0440\u0435\u0432\u0435\u0434\u0438 \u0442\u043e\u0447\u043d\u0443\u044e \u0441\u0443\u043c\u043c\u0443\n"
            "2. \u0421\u0434\u0435\u043b\u0430\u0439 \u0441\u043a\u0440\u0438\u043d\u0448\u043e\u0442 \u0447\u0435\u043a\u0430\n"
            "3. \u041e\u0442\u043f\u0440\u0430\u0432\u044c \u0441\u043a\u0440\u0438\u043d\u0448\u043e\u0442 \u0441\u044e\u0434\u0430 \u0432 \u0447\u0430\u0442\n"
            "4. \u041d\u0430\u0436\u043c\u0438 <b>\u00ab\u042f \u043e\u043f\u043b\u0430\u0442\u0438\u043b\u00bb</b>"
        )
    else:
        markup.add(InlineKeyboardButton("\u2705 \u042f \u043e\u043f\u043b\u0430\u0442\u0438\u043b", callback_data="paid"))
        markup.add(InlineKeyboardButton("\u2b05 \u041d\u0430\u0437\u0430\u0434", callback_data="plan_" + key))
        text = (
            "\U0001f4b0 <b>\u041e\u043f\u043b\u0430\u0442\u0430 USDT</b>\n\n"
            "\U0001f4e6 \u0422\u0430\u0440\u0438\u0444: " + p["title"] + " \u2014 " + str(p["price"]) + "\u20bd\n\n"
            "\u041e\u0442\u043f\u0440\u0430\u0432\u044c \u044d\u043a\u0432\u0438\u0432\u0430\u043b\u0435\u043d\u0442 <b>" + str(p["price"]) + "\u20bd</b> \u0432 USDT \u043d\u0430 \u0430\u0434\u0440\u0435\u0441:\n\n"
            "<code>" + USDT_WALLET + "</code>\n\n"
            "1. \u041f\u0435\u0440\u0435\u0432\u0435\u0434\u0438 \u0442\u043e\u0447\u043d\u0443\u044e \u0441\u0443\u043c\u043c\u0443\n"
            "2. \u0421\u0434\u0435\u043b\u0430\u0439 \u0441\u043a\u0440\u0438\u043d\u0448\u043e\u0442 \u0447\u0435\u043a\u0430\n"
            "3. \u041e\u0442\u043f\u0440\u0430\u0432\u044c \u0441\u043a\u0440\u0438\u043d\u0448\u043e\u0442 \u0441\u044e\u0434\u0430 \u0432 \u0447\u0430\u0442\n"
            "4. \u041d\u0430\u0436\u043c\u0438 <b>\u00ab\u042f \u043e\u043f\u043b\u0430\u0442\u0438\u043b\u00bb</b>"
        )
    safe_edit(call, text, markup)


@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    uid = message.from_user.id
    if uid not in user_state or not user_state[uid].get("plan"):
        return
    if uid in pending_payments:
        return
    user_state[uid]["receipt_file_id"] = message.photo[-1].file_id
    bot.send_message(
        uid,
        "\U0001f4f8 <b>\u0424\u043e\u0442\u043e \u0447\u0435\u043a\u0430 \u043f\u043e\u043b\u0443\u0447\u0435\u043d\u043e!</b>\n\n"
        "\u0422\u0435\u043f\u0435\u0440\u044c \u043d\u0430\u0436\u043c\u0438 \u043a\u043d\u043e\u043f\u043a\u0443 <b>\u00ab\u042f \u043e\u043f\u043b\u0430\u0442\u0438\u043b\u00bb</b> \u0432 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0438 \u0432\u044b\u0448\u0435.",
        parse_mode="HTML",
    )


@bot.callback_query_handler(func=lambda c: c.data == "paid")
def cb_paid(call):
    uid = call.from_user.id
    state = user_state.get(uid)
    if not state or not state.get("plan"):
        answer(call, "\u041e\u0448\u0438\u0431\u043a\u0430: \u0441\u043d\u0430\u0447\u0430\u043b\u0430 \u0432\u044b\u0431\u0435\u0440\u0438 \u0442\u0430\u0440\u0438\u0444")
        return
    if uid in pending_payments:
        answer(call, "\u26a0\ufe0f \u0417\u0430\u044f\u0432\u043a\u0430 \u0443\u0436\u0435 \u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0430, \u043e\u0436\u0438\u0434\u0430\u0439 \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u044f")
        return
    if not state.get("receipt_file_id"):
        answer(call, "\U0001f4f8 \u0421\u043d\u0430\u0447\u0430\u043b\u0430 \u043e\u0442\u043f\u0440\u0430\u0432\u044c \u0444\u043e\u0442\u043e \u0447\u0435\u043a\u0430!")
        bot.send_message(
            uid,
            "\u2757 <b>\u041d\u0443\u0436\u043d\u043e \u043e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c \u0444\u043e\u0442\u043e \u0447\u0435\u043a\u0430</b>\n\n"
            "\u0421\u0434\u0435\u043b\u0430\u0439 \u0441\u043a\u0440\u0438\u043d\u0448\u043e\u0442 \u043e\u043f\u043b\u0430\u0442\u044b, \u043e\u0442\u043f\u0440\u0430\u0432\u044c \u0435\u0433\u043e \u0441\u044e\u0434\u0430 \u0432 \u0447\u0430\u0442, "
            "\u0437\u0430\u0442\u0435\u043c \u043d\u0430\u0436\u043c\u0438 <b>\u00ab\u042f \u043e\u043f\u043b\u0430\u0442\u0438\u043b\u00bb</b>.",
            parse_mode="HTML",
        )
        return
    plan_key = state["plan"]
    method = state.get("method", "unknown")
    p = PLANS[plan_key]
    username = call.from_user.username or "\u043d\u0435\u0442"
    pending_payments[uid] = {"plan": plan_key, "method": method, "receipt_file_id": state["receipt_file_id"]}
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("\u23f3 \u041e\u0436\u0438\u0434\u0430\u0439 \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u044f...", callback_data="wait"))
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    except Exception:
        pass
    method_names = {"boosty": "Boosty", "card": "\u041a\u0430\u0440\u0442\u0430", "usdt": "USDT"}
    caption = (
        "\U0001f4b0 <b>\u041d\u043e\u0432\u0430\u044f \u0437\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0443!</b>\n\n"
        "\U0001f464 ID: <code>" + str(uid) + "</code>\n"
        "\U0001f464 Username: @" + username + "\n"
        "\U0001f4e6 \u0422\u0430\u0440\u0438\u0444: " + p["title"] + " (" + p["duration"] + ") \u2014 " + str(p["price"]) + "\u20bd\n"
        "\U0001f4b3 \u0421\u043f\u043e\u0441\u043e\u0431: " + method_names.get(method, method)
    )
    admin_markup = InlineKeyboardMarkup()
    admin_markup.add(InlineKeyboardButton("\u2705 \u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0434\u0438\u0442\u044c", callback_data="confirm_" + str(uid)))
    admin_markup.add(InlineKeyboardButton("\u274c \u041e\u0442\u043a\u043b\u043e\u043d\u0438\u0442\u044c", callback_data="reject_" + str(uid)))
    try:
        bot.send_photo(ADMIN_ID, state["receipt_file_id"], caption=caption, reply_markup=admin_markup, parse_mode="HTML")
    except Exception as e:
        print("send photo to admin error:", e)
        bot.send_message(ADMIN_ID, caption, reply_markup=admin_markup, parse_mode="HTML")
    answer(call, "\u2705 \u0417\u0430\u044f\u0432\u043a\u0430 \u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0430")


@bot.callback_query_handler(func=lambda c: c.data == "wait")
def cb_wait(call):
    answer(call, "\u23f3 \u041e\u0436\u0438\u0434\u0430\u0439 \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u044f \u043e\u0442 \u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440\u0430")


@bot.callback_query_handler(func=lambda c: c.data.startswith("confirm_"))
def cb_confirm(call):
    if call.from_user.id != ADMIN_ID:
        answer(call, "\u274c \u041d\u0435\u0442 \u0434\u043e\u0441\u0442\u0443\u043f\u0430")
        return
    uid = int(call.data.split("_")[1])
    if uid not in pending_payments:
        answer(call, "\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u0430")
        return
    data = pending_payments.pop(uid)
    plan_key = data["plan"]
    plan = PLANS[plan_key]
    if plan["vip"]:
        expire = datetime.now() + timedelta(days=plan["days"])
    else:
        existing = subs.get(uid)
        if existing and existing["expire"] > datetime.now():
            expire = existing["expire"] + timedelta(days=plan["days"])
        else:
            expire = datetime.now() + timedelta(days=plan["days"])
    subs[uid] = {"expire": expire, "plan": plan_key}
    user_state.pop(uid, None)
    invite_channel, invite_chat = add_user_to_channels(uid, plan_key)
    user_markup = InlineKeyboardMarkup()
    if invite_channel:
        label = "\U0001f451 \u0412\u043e\u0439\u0442\u0438 \u0432 VIP \u043a\u0430\u043d\u0430\u043b" if plan["vip"] else "\U0001f680 \u0412\u043e\u0439\u0442\u0438 \u0432 \u043a\u0430\u043d\u0430\u043b"
        user_markup.add(InlineKeyboardButton(label, url=invite_channel))
    if invite_chat:
        label = "\U0001f451 \u0412\u043e\u0439\u0442\u0438 \u0432 VIP \u0447\u0430\u0442" if plan["vip"] else "\U0001f4ac \u0412\u043e\u0439\u0442\u0438 \u0432 \u0447\u0430\u0442"
        user_markup.add(InlineKeyboardButton(label, url=invite_chat))
    user_markup.add(InlineKeyboardButton("\U0001f4cb \u0413\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e", callback_data="menu"))
    try:
        bot.send_message(
            uid,
            "\u2705 <b>\u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0430 \u043e\u0434\u043e\u0431\u0440\u0435\u043d\u0430, \u0434\u043e\u0431\u0440\u043e \u043f\u043e\u0436\u0430\u043b\u043e\u0432\u0430\u0442\u044c!</b>\n\n"
            "\U0001f4e6 \u0422\u0430\u0440\u0438\u0444: " + plan["title"] + "\n"
            "\U0001f4c5 \u0414\u0435\u0439\u0441\u0442\u0432\u0443\u0435\u0442 \u0434\u043e: " + expire.strftime("%d.%m.%Y %H:%M") + "\n\n"
            "\u041d\u0430\u0436\u043c\u0438 \u043a\u043d\u043e\u043f\u043a\u0443 \u043d\u0438\u0436\u0435 \u0447\u0442\u043e\u0431\u044b \u0432\u043e\u0439\u0442\u0438:",
            reply_markup=user_markup,
            parse_mode="HTML",
        )
    except Exception as e:
        print("send confirm to user error:", e)
    try:
        bot.edit_message_caption(
            caption="\u2705 <b>\u041f\u041e\u0414\u0422\u0412\u0415\u0420\u0416\u0414\u0415\u041d\u041e</b>\nUser: <code>" + str(uid) + "</code>\n\u0422\u0430\u0440\u0438\u0444: " + plan["title"],
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML",
        )
    except Exception:
        try:
            bot.edit_message_text(
                "\u2705 <b>\u041f\u041e\u0414\u0422\u0412\u0415\u0420\u0416\u0414\u0415\u041d\u041e</b>\nUser: <code>" + str(uid) + "</code>\n\u0422\u0430\u0440\u0438\u0444: " + plan["title"],
                call.message.chat.id, call.message.message_id, parse_mode="HTML",
            )
        except Exception as e:
            print("edit admin confirm error:", e)
    answer(call, "\u2705 \u0413\u043e\u0442\u043e\u0432\u043e!")


@bot.callback_query_handler(func=lambda c: c.data.startswith("reject_"))
def cb_reject(call):
    if call.from_user.id != ADMIN_ID:
        answer(call, "\u274c \u041d\u0435\u0442 \u0434\u043e\u0441\u0442\u0443\u043f\u0430")
        return
    uid = int(call.data.split("_")[1])
    pending_payments.pop(uid, None)
    user_state.pop(uid, None)
    try:
        bot.send_message(
            uid,
            "\u274c <b>\u0412\u0430\u0448 \u0437\u0430\u043f\u0440\u043e\u0441 \u043e\u0442\u043a\u043b\u043e\u043d\u0451\u043d \u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440\u043e\u043c</b>\n\n"
            "\u041f\u043e \u0432\u043e\u043f\u0440\u043e\u0441\u0430\u043c \u0441\u0432\u044f\u0436\u0438\u0442\u0435\u0441\u044c: @" + ADMIN_USERNAME,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("\U0001f4cb \u0413\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e", callback_data="menu")
            ),
        )
    except Exception as e:
        print("send reject to user error:", e)
    try:
        bot.edit_message_caption(
            caption="\u274c <b>\u041e\u0422\u041a\u041b\u041e\u041d\u0415\u041d\u041e</b>\nUser: <code>" + str(uid) + "</code>",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML",
        )
    except Exception:
        try:
            bot.edit_message_text(
                "\u274c <b>\u041e\u0422\u041a\u041b\u041e\u041d\u0415\u041d\u041e</b>\nUser: <code>" + str(uid) + "</code>",
                call.message.chat.id, call.message.message_id, parse_mode="HTML",
            )
        except Exception as e:
            print("edit admin reject error:", e)
    answer(call, "\u041e\u0442\u043a\u043b\u043e\u043d\u0435\u043d\u043e")


def background_worker():
    notified_2d = set()
    notified_1d = set()
    while True:
        now = datetime.now()
        for uid, sub in list(subs.items()):
            remaining = sub["expire"] - now
            if timedelta(days=1, hours=23) < remaining <= timedelta(days=2) and uid not in notified_2d:
                notified_2d.add(uid)
                try:
                    bot.send_message(
                        uid,
                        "\u23f0 <b>\u0414\u043e \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0438 \u043e\u0441\u0442\u0430\u043b\u043e\u0441\u044c 2 \u0434\u043d\u044f!</b>\n\n"
                        "\u041f\u0440\u043e\u0434\u043b\u0438 \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0443 \u0447\u0442\u043e\u0431\u044b \u043d\u0435 \u043f\u043e\u0442\u0435\u0440\u044f\u0442\u044c \u0434\u043e\u0441\u0442\u0443\u043f.",
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup().add(
                            InlineKeyboardButton("\U0001f4b0 \u041f\u0440\u043e\u0434\u043b\u0438\u0442\u044c", callback_data="tariffs")
                        ),
                    )
                except Exception as e:
                    print("notify 2d error:", e)
            elif timedelta(hours=23) < remaining <= timedelta(days=1) and uid not in notified_1d:
                notified_1d.add(uid)
                try:
                    bot.send_message(
                        uid,
                        "\u26a0\ufe0f <b>\u0414\u043e \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0438 \u043e\u0441\u0442\u0430\u043b\u0441\u044f 1 \u0434\u0435\u043d\u044c!</b>\n\n"
                        "\u0421\u0440\u043e\u0447\u043d\u043e \u043f\u0440\u043e\u0434\u043b\u0438 \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0443 \u0447\u0442\u043e\u0431\u044b \u0441\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u0434\u043e\u0441\u0442\u0443\u043f.",
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup().add(
                            InlineKeyboardButton("\U0001f4b0 \u041f\u0440\u043e\u0434\u043b\u0438\u0442\u044c", callback_data="tariffs")
                        ),
                    )
                except Exception as e:
                    print("notify 1d error:", e)
            elif remaining.total_seconds() <= 0:
                plan_key = sub["plan"]
                kick_user_from_channels(uid, plan_key)
                try:
                    bot.send_message(
                        uid,
                        "\u23f0 <b>\u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0430 \u0438\u0441\u0442\u0435\u043a\u043b\u0430</b>\n\n"
                        "\u0422\u044b \u0431\u044b\u043b \u0443\u0434\u0430\u043b\u0451\u043d \u0438\u0437 \u043a\u0430\u043d\u0430\u043b\u0430.\n"
                        "\u041d\u0430\u0436\u043c\u0438 \u043a\u043d\u043e\u043f\u043a\u0443 \u0447\u0442\u043e\u0431\u044b \u043f\u0440\u043e\u0434\u043b\u0438\u0442\u044c \u0434\u043e\u0441\u0442\u0443\u043f.",
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup().add(
                            InlineKeyboardButton("\U0001f4b0 \u041f\u0440\u043e\u0434\u043b\u0438\u0442\u044c", callback_data="tariffs")
                        ),
                    )
                except Exception as e:
                    print("expire notify error:", e)
                subs.pop(uid, None)
                notified_2d.discard(uid)
                notified_1d.discard(uid)
        time.sleep(600)


threading.Thread(target=background_worker, daemon=True).start()

print("BOT STARTED")
bot.infinity_polling(skip_pending=True)
ENDOFFILE