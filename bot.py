
import telebot
import os
import threading
import time
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================================================================

# ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ — задай их в хостинге

# 

# TOKEN              — токен бота от @BotFather

# ADMIN_ID           — твой Telegram ID (число, узнать у @userinfobot)

# ADMIN_USERNAME     — твой username без @ (например: myusername)

# CARD_NUMBER        — номер карты для оплаты

# USDT_WALLET        — адрес USDT кошелька

# BOOSTY_URL         — ссылка на твою страницу Boosty (https://boosty.to/…)

# TRIAL_CHANNEL_URL  — ссылка на пробный канал (https://t.me/+…)

# CHANNEL_ID         — ID обычного канала (1-3 уровень), число со знаком минус

# CHAT_ID            — ID обычного чата (3 уровень), число со знаком минус

# VIP_CHANNEL_ID     — ID VIP канала (4 уровень), число со знаком минус

# VIP_CHAT_ID        — ID VIP чата (4 уровень), число со знаком минус

# TIKTOK_URL         — ссылка на TikTok (https://tiktok.com/@…)

# INSTAGRAM_URL      — ссылка на Instagram (https://instagram.com/…)

# MAIN_CHANNEL_URL   — ссылка на основной Telegram канал (https://t.me/…)

# ================================================================

TOKEN             = os.environ[“TOKEN”]
ADMIN_ID          = int(os.environ[“ADMIN_ID”])
ADMIN_USERNAME    = os.environ.get(“ADMIN_USERNAME”, “admin”)
CARD_NUMBER       = os.environ.get(“CARD_NUMBER”, “0000 0000 0000 0000”)
USDT_WALLET       = os.environ.get(“USDT_WALLET”, “wallet_address”)
BOOSTY_URL        = os.environ.get(“BOOSTY_URL”, “https://boosty.to/”)
TRIAL_CHANNEL_URL = os.environ.get(“TRIAL_CHANNEL_URL”, “https://t.me/”)
CHANNEL_ID        = int(os.environ[“CHANNEL_ID”])
CHAT_ID           = int(os.environ[“CHAT_ID”])
VIP_CHANNEL_ID    = int(os.environ[“VIP_CHANNEL_ID”])
VIP_CHAT_ID       = int(os.environ[“VIP_CHAT_ID”])
TIKTOK_URL        = os.environ.get(“TIKTOK_URL”, “https://tiktok.com/”)
INSTAGRAM_URL     = os.environ.get(“INSTAGRAM_URL”, “https://instagram.com/”)
MAIN_CHANNEL_URL  = os.environ.get(“MAIN_CHANNEL_URL”, “https://t.me/”)

bot = telebot.TeleBot(TOKEN)

# ================================================================

# ХРАНИЛИЩЕ (в памяти, сбрасывается при перезапуске)

# ================================================================

subs             = {}   # uid -> {“expire”: datetime, “plan”: str}
pending_payments = {}   # uid -> {“plan”: str, “method”: str, “receipt_file_id”: str}
user_state       = {}   # uid -> {“plan”: str, “method”: str, “receipt_file_id”: str}

# ================================================================

# ТАРИФЫ

# ================================================================

PLANS = {
“lvl1”: {
“days”: 1,
“price”: 600,
“title”: “1 уровень”,
“duration”: “1 день”,
“vip”: False,
“description”: (
“1️⃣ <b>1 уровень — 600₽ / 1 день</b>\n\n”
“✅ Доступ к закрытому каналу\n”
“✅ Весь контент за день\n\n”
“Идеально чтобы познакомиться с материалом.”
),
},
“lvl2”: {
“days”: 7,
“price”: 1590,
“title”: “2 уровень”,
“duration”: “1 неделя”,
“vip”: False,
“description”: (
“2️⃣ <b>2 уровень — 1590₽ / 1 неделя</b>\n\n”
“✅ Доступ к закрытому каналу\n”
“✅ Весь контент за неделю\n\n”
“Отличный старт для погружения.”
),
},
“lvl3”: {
“days”: 30,
“price”: 2690,
“title”: “3 уровень”,
“duration”: “1 месяц”,
“vip”: False,
“description”: (
“3️⃣ <b>3 уровень — 2690₽ / 1 месяц</b>\n\n”
“✅ Доступ к закрытому каналу\n”
“✅ Доступ к закрытому чату\n”
“✅ Весь контент за месяц\n\n”
“Максимум пользы на месяц вперёд.”
),
},
“lvl4”: {
“days”: 30,
“price”: 4990,
“title”: “4 уровень (VIP)”,
“duration”: “1 месяц”,
“vip”: True,
“description”: (
“👑 <b>4 уровень VIP — 4990₽ / 1 месяц</b>\n\n”
“✅ Доступ к VIP каналу\n”
“✅ Доступ к VIP чату\n”
“✅ Эксклюзивный контент\n”
“✅ Прямая связь\n\n”
“⚠️ <b>Внимание:</b> при покупке VIP все предыдущие “
“подписки аннулируются и заменяются на VIP на 1 месяц.”
),
},
}

# ================================================================

# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ

# ================================================================

def answer(call, text=””):
try:
bot.answer_callback_query(call.id, text)
except Exception:
pass

def safe_edit(call, text, markup=None):
try:
bot.edit_message_text(
text,
call.message.chat.id,
call.message.message_id,
reply_markup=markup,
parse_mode=“HTML”,
)
except Exception as e:
print(“safe_edit:”, e)

def menu_btn():
m = InlineKeyboardMarkup()
m.add(InlineKeyboardButton(“⬅ Назад в меню”, callback_data=“menu”))
return m

def add_user_to_channels(uid, plan_key):
“”“Создаёт одноразовые ссылки для входа в нужные каналы/чаты”””
plan = PLANS[plan_key]
invite_channel = None
invite_chat    = None

```
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
```

def kick_user_from_channels(uid, plan_key):
“”“Выкидывает пользователя из всех его каналов”””
plan = PLANS[plan_key]
targets = []

```
if plan["vip"]:
    targets = [VIP_CHANNEL_ID, VIP_CHAT_ID]
else:
    targets = [CHANNEL_ID]
    if plan_key == "lvl3":
        targets.append(CHAT_ID)

for chat in targets:
    try:
        bot.ban_chat_member(chat, uid)
        bot.unban_chat_member(chat, uid)
    except Exception as e:
        print(f"kick error uid={uid} chat={chat}:", e)
```

# ================================================================

# ГЛАВНОЕ МЕНЮ

# ================================================================

def show_menu(chat_id, message_id=None):
markup = InlineKeyboardMarkup()
markup.add(InlineKeyboardButton(“💰 Список тарифов”,    callback_data=“tariffs”))
markup.add(InlineKeyboardButton(“🎥 Пробное видео”,     callback_data=“trial”))
markup.add(InlineKeyboardButton(“📊 Проверка подписки”, callback_data=“check”))
markup.add(InlineKeyboardButton(“🔗 Ссылки на меня”,    callback_data=“links”))

```
text = (
    "👋 <b>Добро пожаловать!</b>\n\n"
    "Здесь ты можешь оформить подписку, "
    "посмотреть пробное видео или проверить статус своей подписки.\n\n"
    "Выбери нужный раздел:"
)

if message_id:
    try:
        bot.edit_message_text(
            text, chat_id, message_id,
            reply_markup=markup, parse_mode="HTML"
        )
        return
    except Exception:
        pass

bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
```

@bot.message_handler(commands=[“start”])
def cmd_start(message):
show_menu(message.chat.id)

@bot.callback_query_handler(func=lambda c: c.data == “menu”)
def cb_menu(call):
answer(call)
show_menu(call.message.chat.id, call.message.message_id)

# ================================================================

# ССЫЛКИ НА МЕНЯ

# ================================================================

@bot.callback_query_handler(func=lambda c: c.data == “links”)
def cb_links(call):
answer(call)
markup = InlineKeyboardMarkup()
markup.add(InlineKeyboardButton(“🎵 TikTok”,          url=TIKTOK_URL))
markup.add(InlineKeyboardButton(“📸 Instagram”,       url=INSTAGRAM_URL))
markup.add(InlineKeyboardButton(“🚀 Boosty”,          url=BOOSTY_URL))
markup.add(InlineKeyboardButton(“📢 Основной канал”,  url=MAIN_CHANNEL_URL))
markup.add(InlineKeyboardButton(“💬 Связь со мной”,   url=f”https://t.me/{ADMIN_USERNAME}”))
markup.add(InlineKeyboardButton(“⬅ Назад”,           callback_data=“menu”))

```
safe_edit(call, "🔗 <b>Мои ссылки</b>\n\nВыбери куда перейти:", markup)
```

# ================================================================

# ПРОБНОЕ ВИДЕО

# ================================================================

@bot.callback_query_handler(func=lambda c: c.data == “trial”)
def cb_trial(call):
answer(call)
markup = InlineKeyboardMarkup()
markup.add(InlineKeyboardButton(“🎧 Надень наушники”, url=TRIAL_CHANNEL_URL))
markup.add(InlineKeyboardButton(“⬅ Назад”,           callback_data=“menu”))

```
safe_edit(
    call,
    "🎥 <b>Пробное видео</b>\n\n"
    "Надень наушники и нажми кнопку ниже — "
    "тебя перенесёт в канал с пробным видео.\n\n"
    "⏳ Доступ открыт на <b>24 часа</b>.",
    markup,
)
```

# ================================================================

# ПРОВЕРКА ПОДПИСКИ

# ================================================================

@bot.callback_query_handler(func=lambda c: c.data == “check”)
def cb_check(call):
answer(call)
uid = call.from_user.id
sub = subs.get(uid)

```
if not sub or (sub["expire"] - datetime.now()).total_seconds() <= 0:
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💰 Купить подписку", callback_data="tariffs"))
    markup.add(InlineKeyboardButton("⬅ Назад",           callback_data="menu"))
    safe_edit(call, "❌ <b>Нет активных подписок</b>\n\nОформи подписку чтобы получить доступ.", markup)
    return

remaining = sub["expire"] - datetime.now()
days      = remaining.days
hours     = remaining.seconds // 3600
p         = PLANS[sub["plan"]]

safe_edit(
    call,
    f"✅ <b>Подписка активна</b>\n\n"
    f"📦 Тариф: {p['title']}\n"
    f"⏳ Осталось: {days} дн. {hours} ч.\n"
    f"📅 До: {sub['expire'].strftime('%d.%m.%Y %H:%M')}",
    menu_btn(),
)
```

# ================================================================

# СПИСОК ТАРИФОВ

# ================================================================

@bot.callback_query_handler(func=lambda c: c.data == “tariffs”)
def cb_tariffs(call):
answer(call)
markup = InlineKeyboardMarkup()
markup.add(InlineKeyboardButton(“1️⃣  600₽  — 1 день”,    callback_data=“plan_lvl1”))
markup.add(InlineKeyboardButton(“2️⃣  1590₽ — 1 неделя”,  callback_data=“plan_lvl2”))
markup.add(InlineKeyboardButton(“3️⃣  2690₽ — 1 месяц”,   callback_data=“plan_lvl3”))
markup.add(InlineKeyboardButton(“👑  4990₽ — VIP месяц”,  callback_data=“plan_lvl4”))
markup.add(InlineKeyboardButton(“⬅ Назад”,               callback_data=“menu”))

```
safe_edit(call, "💰 <b>Выбери тариф</b>\n\nНажми на тариф чтобы увидеть описание:", markup)
```

# ================================================================

# ОПИСАНИЕ ТАРИФА + ВЫБОР СПОСОБА ОПЛАТЫ

# ================================================================

@bot.callback_query_handler(func=lambda c: c.data.startswith(“plan_”))
def cb_plan(call):
answer(call)
uid = call.from_user.id
key = call.data[5:]

```
if key not in PLANS:
    return

user_state[uid] = {"plan": key, "method": None, "receipt_file_id": None}
p = PLANS[key]

markup = InlineKeyboardMarkup()
markup.add(InlineKeyboardButton("🚀 Boosty", callback_data=f"method_boosty_{key}"))
markup.add(InlineKeyboardButton("💳 Карта",  callback_data=f"method_card_{key}"))
markup.add(InlineKeyboardButton("💰 USDT",   callback_data=f"method_usdt_{key}"))
markup.add(InlineKeyboardButton("⬅ Назад",  callback_data="tariffs"))

safe_edit(call, p["description"] + "\n\n💳 <b>Выбери способ оплаты:</b>", markup)
```

# ================================================================

# ЭКРАН РЕКВИЗИТОВ

# ================================================================

@bot.callback_query_handler(func=lambda c: c.data.startswith(“method_”))
def cb_method(call):
answer(call)
uid = call.from_user.id

```
if uid in pending_payments:
    answer(call, "⚠️ У тебя уже есть активная заявка, ожидай подтверждения")
    return

parts  = call.data.split("_")   # ["method", "boosty/card/usdt", "lvlX"]
method = parts[1]
key    = parts[2]

if key not in PLANS:
    return

user_state[uid] = {"plan": key, "method": method, "receipt_file_id": None}
p = PLANS[key]

markup = InlineKeyboardMarkup()

if method == "boosty":
    markup.add(InlineKeyboardButton("💳 Перейти к оплате", url=BOOSTY_URL))
    markup.add(InlineKeyboardButton("✅ Я оплатил",        callback_data="paid"))
    markup.add(InlineKeyboardButton("⬅ Назад",            callback_data=f"plan_{key}"))

    text = (
        f"🚀 <b>Оплата через Boosty</b>\n\n"
        f"📦 Тариф: {p['title']} — {p['price']}₽\n\n"
        f"1. Нажми <b>«Перейти к оплате»</b>\n"
        f"2. Оформи подписку на Boosty\n"
        f"3. Сделай скриншот чека\n"
        f"4. Отправь скриншот сюда в чат\n"
        f"5. Нажми <b>«Я оплатил»</b>"
    )

elif method == "card":
    markup.add(InlineKeyboardButton("✅ Я оплатил", callback_data="paid"))
    markup.add(InlineKeyboardButton("⬅ Назад",     callback_data=f"plan_{key}"))

    text = (
        f"💳 <b>Оплата картой</b>\n\n"
        f"📦 Тариф: {p['title']} — {p['price']}₽\n\n"
        f"Переведи <b>{p['price']}₽</b> на карту:\n\n"
        f"<code>{CARD_NUMBER}</code>\n\n"
        f"1. Переведи точную сумму\n"
        f"2. Сделай скриншот чека\n"
        f"3. Отправь скриншот сюда в чат\n"
        f"4. Нажми <b>«Я оплатил»</b>"
    )

else:  # usdt
    markup.add(InlineKeyboardButton("✅ Я оплатил", callback_data="paid"))
    markup.add(InlineKeyboardButton("⬅ Назад",     callback_data=f"plan_{key}"))

    text = (
        f"💰 <b>Оплата USDT</b>\n\n"
        f"📦 Тариф: {p['title']} — {p['price']}₽\n\n"
        f"Отправь эквивалент <b>{p['price']}₽</b> в USDT на адрес:\n\n"
        f"<code>{USDT_WALLET}</code>\n\n"
        f"1. Переведи точную сумму\n"
        f"2. Сделай скриншот чека\n"
        f"3. Отправь скриншот сюда в чат\n"
        f"4. Нажми <b>«Я оплатил»</b>"
    )

safe_edit(call, text, markup)
```

# ================================================================

# ПРИЁМ ФОТО ЧЕКА ОТ ПОЛЬЗОВАТЕЛЯ

# ================================================================

@bot.message_handler(content_types=[“photo”])
def handle_photo(message):
uid = message.from_user.id

```
if uid not in user_state or not user_state[uid].get("plan"):
    return

if uid in pending_payments:
    return

user_state[uid]["receipt_file_id"] = message.photo[-1].file_id

bot.send_message(
    uid,
    "📸 <b>Фото чека получено!</b>\n\n"
    "Теперь нажми кнопку <b>«Я оплатил»</b> в сообщении выше.",
    parse_mode="HTML",
)
```

# ================================================================

# ПОЛЬЗОВАТЕЛЬ НАЖАЛ «Я ОПЛАТИЛ»

# ================================================================

@bot.callback_query_handler(func=lambda c: c.data == “paid”)
def cb_paid(call):
uid   = call.from_user.id
state = user_state.get(uid)

```
if not state or not state.get("plan"):
    answer(call, "Ошибка: сначала выбери тариф")
    return

if uid in pending_payments:
    answer(call, "⚠️ Заявка уже отправлена, ожидай подтверждения")
    return

if not state.get("receipt_file_id"):
    answer(call, "📸 Сначала отправь фото чека!")
    bot.send_message(
        uid,
        "❗ <b>Нужно отправить фото чека</b>\n\n"
        "Сделай скриншот оплаты, отправь его сюда в чат, "
        "затем нажми <b>«Я оплатил»</b>.",
        parse_mode="HTML",
    )
    return

plan_key = state["plan"]
method   = state.get("method", "неизвестно")
p        = PLANS[plan_key]
username = call.from_user.username or "нет"

pending_payments[uid] = {
    "plan":             plan_key,
    "method":           method,
    "receipt_file_id":  state["receipt_file_id"],
}

# блокируем кнопки у пользователя
markup = InlineKeyboardMarkup()
markup.add(InlineKeyboardButton("⏳ Ожидай подтверждения...", callback_data="wait"))
try:
    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
    )
except Exception:
    pass

method_names = {"boosty": "Boosty", "card": "Карта", "usdt": "USDT"}
caption = (
    f"💰 <b>Новая заявка на подписку!</b>\n\n"
    f"👤 ID: <code>{uid}</code>\n"
    f"👤 Username: @{username}\n"
    f"📦 Тариф: {p['title']} ({p['duration']}) — {p['price']}₽\n"
    f"💳 Способ: {method_names.get(method, method)}"
)

admin_markup = InlineKeyboardMarkup()
admin_markup.add(InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_{uid}"))
admin_markup.add(InlineKeyboardButton("❌ Отклонить",   callback_data=f"reject_{uid}"))

try:
    bot.send_photo(
        ADMIN_ID,
        state["receipt_file_id"],
        caption=caption,
        reply_markup=admin_markup,
        parse_mode="HTML",
    )
except Exception as e:
    print("send photo to admin error:", e)
    bot.send_message(ADMIN_ID, caption, reply_markup=admin_markup, parse_mode="HTML")

answer(call, "✅ Заявка отправлена")
```

# ================================================================

# КНОПКА «WAIT»

# ================================================================

@bot.callback_query_handler(func=lambda c: c.data == “wait”)
def cb_wait(call):
answer(call, “⏳ Ожидай подтверждения от администратора”)

# ================================================================

# АДМИН: ПОДТВЕРДИТЬ

# ================================================================

@bot.callback_query_handler(func=lambda c: c.data.startswith(“confirm_”))
def cb_confirm(call):
if call.from_user.id != ADMIN_ID:
answer(call, “❌ Нет доступа”)
return

```
uid = int(call.data.split("_")[1])

if uid not in pending_payments:
    answer(call, "Заявка не найдена")
    return

data     = pending_payments.pop(uid)
plan_key = data["plan"]
plan     = PLANS[plan_key]

# VIP сбрасывает старую подписку, остальные складываются
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

# сообщение пользователю
user_markup = InlineKeyboardMarkup()
if invite_channel:
    label = "👑 Войти в VIP канал" if plan["vip"] else "🚀 Войти в канал"
    user_markup.add(InlineKeyboardButton(label, url=invite_channel))
if invite_chat:
    label = "👑 Войти в VIP чат" if plan["vip"] else "💬 Войти в чат"
    user_markup.add(InlineKeyboardButton(label, url=invite_chat))
user_markup.add(InlineKeyboardButton("📋 Главное меню", callback_data="menu"))

try:
    bot.send_message(
        uid,
        f"✅ <b>Подписка одобрена, добро пожаловать!</b>\n\n"
        f"📦 Тариф: {plan['title']}\n"
        f"📅 Действует до: {expire.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"Нажми кнопку ниже чтобы войти:",
        reply_markup=user_markup,
        parse_mode="HTML",
    )
except Exception as e:
    print("send confirm to user error:", e)

# обновляем сообщение у админа (оно с фото — edit_message_caption)
try:
    bot.edit_message_caption(
        caption=f"✅ <b>ПОДТВЕРЖДЕНО</b>\nUser: <code>{uid}</code>\nТариф: {plan['title']}",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="HTML",
    )
except Exception:
    try:
        bot.edit_message_text(
            f"✅ <b>ПОДТВЕРЖДЕНО</b>\nUser: <code>{uid}</code>\nТариф: {plan['title']}",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
        )
    except Exception as e:
        print("edit admin msg error:", e)

answer(call, "✅ Готово!")
```

# ================================================================

# АДМИН: ОТКЛОНИТЬ

# ================================================================

@bot.callback_query_handler(func=lambda c: c.data.startswith(“reject_”))
def cb_reject(call):
if call.from_user.id != ADMIN_ID:
answer(call, “❌ Нет доступа”)
return

```
uid = int(call.data.split("_")[1])
pending_payments.pop(uid, None)
user_state.pop(uid, None)

try:
    bot.send_message(
        uid,
        f"❌ <b>Ваш запрос отклонён администратором</b>\n\n"
        f"По вопросам свяжитесь: @{ADMIN_USERNAME}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("📋 Главное меню", callback_data="menu")
        ),
    )
except Exception as e:
    print("send reject to user error:", e)

try:
    bot.edit_message_caption(
        caption=f"❌ <b>ОТКЛОНЕНО</b>\nUser: <code>{uid}</code>",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="HTML",
    )
except Exception:
    try:
        bot.edit_message_text(
            f"❌ <b>ОТКЛОНЕНО</b>\nUser: <code>{uid}</code>",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
        )
    except Exception as e:
        print("edit admin reject error:", e)

answer(call, "Отклонено")
```

# ================================================================

# ФОНОВЫЙ ПОТОК: УВЕДОМЛЕНИЯ И АВТОВЫКИДЫВАНИЕ

# ================================================================

def background_worker():
notified_2d = set()
notified_1d = set()

```
while True:
    now = datetime.now()

    for uid, sub in list(subs.items()):
        remaining = sub["expire"] - now

        # уведомление за 2 дня
        if timedelta(days=1, hours=23) < remaining <= timedelta(days=2) and uid not in notified_2d:
            notified_2d.add(uid)
            try:
                bot.send_message(
                    uid,
                    "⏰ <b>До окончания подписки осталось 2 дня!</b>\n\n"
                    "Продли подписку чтобы не потерять доступ.",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("💰 Продлить", callback_data="tariffs")
                    ),
                )
            except Exception as e:
                print(f"notify 2d error {uid}:", e)

        # уведомление за 1 день
        elif timedelta(hours=23) < remaining <= timedelta(days=1) and uid not in notified_1d:
            notified_1d.add(uid)
            try:
                bot.send_message(
                    uid,
                    "⚠️ <b>До окончания подписки остался 1 день!</b>\n\n"
                    "Срочно продли подписку чтобы сохранить доступ.",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("💰 Продлить", callback_data="tariffs")
                    ),
                )
            except Exception as e:
                print(f"notify 1d error {uid}:", e)

        # подписка истекла
        elif remaining.total_seconds() <= 0:
            plan_key = sub["plan"]
            kick_user_from_channels(uid, plan_key)
            try:
                bot.send_message(
                    uid,
                    "⏰ <b>Подписка истекла</b>\n\n"
                    "Ты был удалён из канала.\n"
                    "Нажми кнопку чтобы продлить доступ.",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("💰 Продлить", callback_data="tariffs")
                    ),
                )
            except Exception as e:
                print(f"expire notify error {uid}:", e)

            subs.pop(uid, None)
            notified_2d.discard(uid)
            notified_1d.discard(uid)

    time.sleep(600)  # проверка каждые 10 минут
```

threading.Thread(target=background_worker, daemon=True).start()

# ================================================================

# ЗАПУСК

# ================================================================

print(“✅ BOT STARTED”)
bot.infinity_polling(skip_pending=True)