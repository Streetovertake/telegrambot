import telebot
import os
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------------- INIT ----------------
TOKEN = os.environ["TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
USDT_WALLET = os.environ["USDT_WALLET"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
bot = telebot.TeleBot(TOKEN)

# ---------------- STORAGE ----------------
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

# ---------------- NAV STACK ----------------
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
    except:
        pass

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    show_menu(message.chat.id)

# ---------------- MENU ----------------
def show_menu(chat_id, message_id=None):

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📊 Проверить подписку", callback_data="check"))
    markup.add(InlineKeyboardButton("🎥 Тестовое видео", callback_data="trial"))
    markup.add(InlineKeyboardButton("💰 Список тарифов", callback_data="tariffs"))

    text = "📱 <b>МЕНЮ</b>"

    try:
        if message_id:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
        else:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    except:
        pass

# ---------------- TARIFS ----------------
def show_tariffs(chat_id, message_id=None, user_id=None):

    if user_id:
        push(user_id, "menu")

    markup = InlineKeyboardMarkup()

    for k, v in PLANS.items():
        markup.add(InlineKeyboardButton(
            f"{v['title']} / {v['price']}₽",
            callback_data=f"plan_{k}"
    ))

    markup.add(
        InlineKeyboardButton(
            "⬅ Назад",
            callback_data="back"
        )
    )

    text = "💰 <b>Выбери тариф</b>"

    try:
        if message_id:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
        else:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    except:
        pass
        
#----- 
@bot.callback_query_handler(func=lambda call: call.data == "tariffs")
def tariffs(call):

    push(call.from_user.id, "menu")

    show_tariffs(
        call.message.chat.id,
        call.message.message_id,
        call.from_user.id
    )

# ---------------- PLAN OPEN ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("plan_"))
def plan(call):

    user_id = call.from_user.id
    plan_key = call.data.split("_")[1]

    if plan_key not in PLANS:
        return

    user_state[user_id] = plan_key
    push(user_id, "tariffs")

    plan = PLANS[plan_key]

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💳 Карта", callback_data=f"card_{plan_key}"))
    markup.add(InlineKeyboardButton("💰 USDT", callback_data=f"usdt_{plan_key}"))
    markup.add(InlineKeyboardButton("🚀 Boosty", callback_data=f"boosty_{plan_key}"))
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    text = f"🔥 <b>{plan['title']}</b>\n💸 {plan['price']}₽"

    safe_edit(call, text, markup)

# ---------------- PAY SCREEN ----------------
def pay(call, method, plan_key):

    plan = PLANS.get(plan_key)
    if not plan:
        return

    user_id = call.from_user.id
    user_state[user_id] = plan_key

    push(user_id, f"plan_{plan_key}")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))
    markup.add(InlineKeyboardButton("✅ Я оплатил", callback_data="paid"))

    if method == "usdt":
        text = f"💰 USDT:\n<code>{USDT_WALLET}</code>"
    elif method == "card":
        text = "💳 Карта:\n<code>2202....</code>"
    else:
        text = "🚀 Boosty ссылка"

    safe_edit(call, text, markup)

# ---------------- PAY HANDLERS ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("usdt_"))
def usdt(call):
    pay(call, "usdt", call.data.split("_")[1])

@bot.callback_query_handler(func=lambda call: call.data.startswith("card_"))
def card(call):
    pay(call, "card", call.data.split("_")[1])

@bot.callback_query_handler(func=lambda call: call.data.startswith("boosty_"))
def boosty(call):
    pay(call, "boosty", call.data.split("_")[1])


# ---------------- PAID ----------------
@bot.callback_query_handler(func=lambda call: call.data == "paid")
def paid(call):

    user_id = call.from_user.id
    plan_key = user_state.get(user_id)

    if not plan_key:
        bot.answer_callback_query(call.id, "Ошибка: выбери тариф")
        return

    pending_payments[user_id] = plan_key

    # USER SCREEN
    user_markup = InlineKeyboardMarkup()
    user_markup.add(
        InlineKeyboardButton("📱 В меню", callback_data="menu")
    )

    safe_edit(
        call,
        "⏳ Платеж отправлен\n\nОжидай подтверждения администратора",
        user_markup
    )

    # ADMIN SCREEN
    admin_markup = InlineKeyboardMarkup()
    admin_markup.add(
        InlineKeyboardButton(
            "✅ Подтвердить",
            callback_data=f"confirm_{user_id}"
        )
    )

    bot.send_message(
        ADMIN_ID,
        f"💰 ОПЛАТА\nUser: {user_id}\nPlan: {plan_key}",
        reply_markup=admin_markup
    )

    bot.answer_callback_query(call.id, "Заявка отправлена")

# ---------------- BACK ----------------
@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):

    user_id = call.from_user.id
    prev = pop(user_id)

    if not prev:
        show_menu(
            call.message.chat.id,
            call.message.message_id
        )
        return

    if prev == "menu":

        show_menu(
            call.message.chat.id,
            call.message.message_id
        )

    elif prev == "tariffs":

        show_tariffs(
            call.message.chat.id,
            call.message.message_id,
            call.from_user.id
        )

    elif prev.startswith("plan_"):

        plan_key = prev.split("_")[1]

        user_state[user_id] = plan_key

        plan_data = PLANS[plan_key]

        markup = InlineKeyboardMarkup()

        markup.add(
            InlineKeyboardButton(
                "💳 Карта",
                callback_data=f"card_{plan_key}"
            )
        )

        markup.add(
            InlineKeyboardButton(
                "💰 USDT",
                callback_data=f"usdt_{plan_key}"
            )
        )

        markup.add(
            InlineKeyboardButton(
                "🚀 Boosty",
                callback_data=f"boosty_{plan_key}"
            )
        )

        markup.add(
            InlineKeyboardButton(
                "⬅ Назад",
                callback_data="back"
            )
        )

        safe_edit(
            call,
            f"🔥 <b>{plan_data['title']}</b>\n💸 {plan_data['price']}₽",
            markup
        )

    else:

        show_menu(
            call.message.chat.id,
            call.message.message_id
        )

# ---------------- TRIAL ----------------
@bot.callback_query_handler(func=lambda call: call.data == "trial")
def trial(call):

    push(call.from_user.id, "menu")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    safe_edit(
        call,
        "🎥 Тестовое видео (сюда вставишь ссылку/канал)",
        markup
    )
    
#_____Confirm
# ---------------- CONFIRM ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm(call):

    if call.from_user.id != ADMIN_ID:
        return

    user_id = int(call.data.split("_")[1])

    plan_key = pending_payments.get(user_id)

    if not plan_key:
        bot.answer_callback_query(call.id, "Нет заявки")
        return

    plan = PLANS[plan_key]

    now = datetime.now()

    if user_id in subs:
        current = subs[user_id]["expire"]
        expire = current + timedelta(days=plan["days"]) if current > now else now + timedelta(days=plan["days"])
    else:
        expire = now + timedelta(days=plan["days"])

    subs[user_id] = {
        "expire": expire,
        "plan": plan_key
    }

    # invite link
    invite = bot.create_chat_invite_link(
        chat_id=CHANNEL_ID,
        member_limit=1
    )

    bot.send_message(
        user_id,
        "✅ Оплата подтверждена\n\n🎉 Доступ выдан",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("🚀 Войти", url=invite.invite_link)
        )
    )

    bot.edit_message_text(
        f"✅ Подтверждено\nUser: {user_id}\nPlan: {plan_key}",
        call.message.chat.id,
        call.message.message_id
    )

    pending_payments.pop(user_id, None)

    bot.answer_callback_query(call.id, "Готово")
    
@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("confirm_"))
    
    # ---------- ПРОДЛЕНИЕ ПОДПИСКИ ----------

    now = datetime.now()

    if user_id in subs:
        current_expire = subs[user_id]["expire"]

        if current_expire > now:
            expire = current_expire + timedelta(days=plan["days"])
        else:
            expire = now + timedelta(days=plan["days"])
    else:
        expire = now + timedelta(days=plan["days"])

    subs[user_id] = {
        "expire": expire,
        "plan": plan_key
    }

    # ---------- CREATE INVITE LINK ----------

    invite = bot.create_chat_invite_link(
        chat_id=CHANNEL_ID,
        member_limit=1
    )

    # ---------- USER MESSAGE ----------

    user_markup = InlineKeyboardMarkup()

    user_markup.add(
        InlineKeyboardButton(
            "🚀 Войти в канал",
            url=invite.invite_link
        )
    )

    bot.send_message(
        user_id,
        "✅ Оплата подтверждена администрацией\n\n🎉 Подписка выдана",
        reply_markup=user_markup
    )

    # ---------- ADMIN ----------

    bot.edit_message_text(
        f"✅ Подтверждено\nUser: {user_id}\nPlan: {plan_key}",
        call.message.chat.id,
        call.message.message_id
    )

    pending_payments.pop(user_id, None)

    bot.answer_callback_query(call.id, "Подписка выдана")

#____
@bot.callback_query_handler(func=lambda call: call.data == "check")
def check(call):

    user_id = call.from_user.id

    sub = subs.get(user_id)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    if not sub:

        text = "❌ Активной подписки нет"

    else:

        expire = sub["expire"]
        left = expire - datetime.now()

        days = left.days

        text = (
            f"✅ Подписка: {sub['plan']}\n"
            f"⏳ Осталось дней: {days}"
        )

    safe_edit(call, text, markup)

# ---------------- RUN ----------------
print("BOT STARTED")
bot.infinity_polling(skip_pending=True)