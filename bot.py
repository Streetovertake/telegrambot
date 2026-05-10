import telebot
import os
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ["TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
USDT_WALLET = os.environ["USDT_WALLET"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

bot = telebot.TeleBot(TOKEN)

subs = {}
pending_payments = {}
user_state = {}
nav_stack = {}

# ---------------- PLANS ----------------
PLANS = {
    "basic": {"days": 1, "price": 600, "title": "Basic"},
    "middle": {"days": 7, "price": 1600, "title": "Middle"},
    "hot": {"days": 30, "price": 2500, "title": "HOT"},
    "ahhh": {"days": 30, "price": 4990, "title": "Ahhh"}
}

# ---------------- NAV ----------------
def push(uid, state):
    nav_stack.setdefault(uid, []).append(state)

def pop(uid):
    return nav_stack.get(uid, []).pop() if nav_stack.get(uid) else None

# ---------------- SAFE EDIT ----------------
def safe_edit(call, text, markup=None):
    try:
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="HTML"
        )
    except Exception as e:
    print("ERROR:", e)


# ================= MENU =================
def show_menu(chat_id, message_id=None):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📊 Проверить подписку", callback_data="check"))
    markup.add(InlineKeyboardButton("🎥 Тестовое видео", callback_data="trial"))
    markup.add(InlineKeyboardButton("💰 Список тарифов", callback_data="tariffs"))

    text = "📱 <b>МЕНЮ</b>"

    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


@bot.message_handler(commands=['start'])
def start(message):
    show_menu(message.chat.id)


# ================= TARIFS =================
def show_tariffs(chat_id, message_id=None, user_id=None):

    if user_id:
        push(user_id, "menu")

    markup = InlineKeyboardMarkup()

    for k, v in PLANS.items():
        markup.add(InlineKeyboardButton(
            f"{v['title']} / {v['price']}₽",
            callback_data=f"plan_{k}"
        ))

    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    text = "💰 <b>Выбери тариф</b>"

    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


@bot.callback_query_handler(func=lambda c: c.data == "tariffs")
def tariffs(call):
    push(call.from_user.id, "menu")
    show_tariffs(call.message.chat.id, call.message.message_id, call.from_user.id)


# ================= PLAN =================
@bot.callback_query_handler(func=lambda c: c.data.startswith("plan_"))
def plan(call):

    uid = call.from_user.id
    key = call.data.split("_")[1]

    if key not in PLANS:
        return

    user_state[uid] = key
    push(uid, "tariffs")

    p = PLANS[key]

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💳 Карта", callback_data=f"card_{key}"))
    markup.add(InlineKeyboardButton("💰 USDT", callback_data=f"usdt_{key}"))
    markup.add(InlineKeyboardButton("🚀 Boosty", callback_data=f"boosty_{key}"))
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    safe_edit(call, f"🔥 <b>{p['title']}</b>\n💸 {p['price']}₽", markup)


# ================= PAY =================
def pay(call, method, key):

    uid = call.from_user.id
    user_state[uid] = key
    push(uid, f"plan_{key}")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))
    markup.add(InlineKeyboardButton("✅ Я оплатил", callback_data="paid"))

    if method == "usdt":
        text = f"USDT:\n<code>{USDT_WALLET}</code>"
    elif method == "card":
        text = "Карта:\n<code>2202....</code>"
    else:
        text = "Boosty"

    safe_edit(call, text, markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith("usdt_"))
def usdt(c): pay(c, "usdt", c.data.split("_")[1])

@bot.callback_query_handler(func=lambda c: c.data.startswith("card_"))
def card(c): pay(c, "card", c.data.split("_")[1])

@bot.callback_query_handler(func=lambda c: c.data.startswith("boosty_"))
def boosty(c): pay(c, "boosty", c.data.split("_")[1])


# ================= PAID =================
@bot.callback_query_handler(func=lambda c: c.data == "paid")
def paid(call):

    user_id = call.from_user.id   # 👈 ВОТ ЭТО ДОБАВИТЬ
    plan_key = user_state.get(user_id)

    if not plan:
        bot.answer_callback_query(call.id, "Ошибка")
        return

    pending_payments[uid] = plan

    user_markup = InlineKeyboardMarkup()
    user_markup.add(InlineKeyboardButton("📱 В меню", callback_data="menu"))

    safe_edit(call,
        "⏳ Платеж отправлен\nОжидай подтверждения",
        user_markup
    )

    admin_markup = InlineKeyboardMarkup()

    admin_markup.add(
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_{user_id}")
    )

    admin_markup.add(
        InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user_id}")
    )

    bot.send_message(
        ADMIN_ID,
        f"💰 PAYMENT\nUser: {uid}\nPlan: {plan}",
        reply_markup=admin_markup
    )

#___reject
@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject(call):

    if call.from_user.id != ADMIN_ID:
        return

    user_id = int(call.data.split("_")[1])

    pending_payments.pop(user_id, None)

    # уведомление пользователю
    bot.send_message(
        user_id,
        "❌ Заявка отклонена администратором"
    )

    # обновляем сообщение админа
    bot.edit_message_text(
        f"❌ ОТКЛОНЕНО\nUser: {user_id}",
        call.message.chat.id,
        call.message.message_id
    )

    bot.answer_callback_query(call.id, "Отклонено")

# ================= MENU CALLBACK =================
@bot.callback_query_handler(func=lambda c: c.data == "menu")
def menu_cb(c):
    show_menu(c.message.chat.id, c.message.message_id)


# ================= BACK =================
@bot.callback_query_handler(func=lambda c: c.data == "back")
def back(call):

    uid = call.from_user.id
    prev = pop(uid)

    if not prev:
        show_menu(call.message.chat.id, call.message.message_id)
        return

    if prev == "menu":
        show_menu(call.message.chat.id, call.message.message_id)

    elif prev == "tariffs":
        show_tariffs(call.message.chat.id, call.message.message_id, uid)

    elif prev.startswith("plan_"):
        key = prev.split("_")[1]
        p = PLANS[key]

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💳 Карта", callback_data=f"card_{key}"))
        markup.add(InlineKeyboardButton("💰 USDT", callback_data=f"usdt_{key}"))
        markup.add(InlineKeyboardButton("🚀 Boosty", callback_data=f"boosty_{key}"))
        markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

        safe_edit(call, f"🔥 {p['title']}\n💸 {p['price']}₽", markup)


# ================= TRIAL =================
@bot.callback_query_handler(func=lambda c: c.data == "trial")
def trial(call):

    push(call.from_user.id, "menu")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    safe_edit(call, "🎥 Тестовое видео", markup)


# ================= CONFIRM (ОДИН!) =================
@bot.callback_query_handler(func=lambda c: c.data.startswith("confirm_"))
def confirm(call):

    if call.from_user.id != ADMIN_ID:
        return

    uid = int(call.data.split("_")[1])
    plan_key = pending_payments.get(uid)

    if not plan_key:
        bot.answer_callback_query(call.id, "Нет заявки")
        return

    plan = PLANS[plan_key]

    now = datetime.now()

    if uid in subs and subs[uid]["expire"] > now:
        expire = subs[uid]["expire"] + timedelta(days=plan["days"])
    else:
        expire = now + timedelta(days=plan["days"])

    subs[uid] = {"expire": expire, "plan": plan_key}

    # ---------- INVITE LINK ----------
    invite = bot.create_chat_invite_link(
        chat_id=CHANNEL_ID,
        member_limit=1
    )

# ---------- USER ----------
    user_markup = InlineKeyboardMarkup()

    user_markup.add(
        InlineKeyboardButton("🚀 Присоединиться к каналу", url=invite.invite_link)
    )

    bot.send_message(
        user_id,
        "✅ Заявка одобрена\n\n🎉 Доступ выдан",
        reply_markup=user_markup
)

# ---------- ADMIN ----------
    bot.edit_message_text(
        f"✅ ОДОБРЕНО\nUser: {user_id}",
        call.message.chat.id,
        call.message.message_id
)


    bot.answer_callback_query(call.id, "Подтверждено")


# ================= CHECK =================
@bot.callback_query_handler(func=lambda c: c.data == "check")
def check(call):

    uid = call.from_user.id
    sub = subs.get(uid)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    if not sub:
        text = "❌ Нет подписки"
    else:
        days = (sub["expire"] - datetime.now()).days
        text = f"✅ {sub['plan']}\n⏳ Осталось: {days} дней"

    safe_edit(call, text, markup)


print("BOT STARTED")
bot.infinity_polling(skip_pending=True)