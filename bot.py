
import telebot
import os
import threading
import time
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# –––––––– ENV VARIABLES ––––––––

# Перед запуском задай эти переменные окружения:

# TOKEN       — токен бота от @BotFather

# ADMIN_ID    — твой Telegram ID (число)

# USDT_WALLET — адрес USDT кошелька

# CHANNEL_ID  — ID закрытого канала (число, например -1001234567890)

# CARD_NUMBER — номер карты для оплаты

TOKEN       = os.environ[“TOKEN”]
ADMIN_ID    = int(os.environ[“ADMIN_ID”])
USDT_WALLET = os.environ[“USDT_WALLET”]
CHANNEL_ID  = int(os.environ[“CHANNEL_ID”])   # ✅ ИСПРАВЛЕНО: теперь число
CARD_NUMBER = os.environ.get(“CARD_NUMBER”, “2202 0000 0000 0000”)

bot = telebot.TeleBot(TOKEN)

# –––––––– ХРАНИЛИЩЕ ––––––––

subs             = {}   # uid -> {“expire”: datetime, “plan”: str}
pending_payments = {}   # uid -> plan_key
user_state       = {}   # uid -> plan_key (последний выбранный тариф)

# –––––––– ТАРИФЫ ––––––––

PLANS = {
“basic”:  {“days”: 1,  “price”: 600,  “title”: “Basic”},
“middle”: {“days”: 7,  “price”: 1600, “title”: “Middle”},
“hot”:    {“days”: 30, “price”: 2500, “title”: “HOT”},
“ahhh”:   {“days”: 30, “price”: 4990, “title”: “Ahhh”},
}

# ================================================================

# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ

# ================================================================

def make_back_btn():
“”“Кнопка Назад в меню”””
markup = InlineKeyboardMarkup()
markup.add(InlineKeyboardButton(“⬅ Назад”, callback_data=“menu”))
return markup

def safe_edit(call, text, markup=None):
“”“Редактирует сообщение, не падает если текст не изменился”””
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

def answer(call, text=””):
“”“Убирает крутилку на кнопке”””
try:
bot.answer_callback_query(call.id, text)
except Exception:
pass

# ================================================================

# ГЛАВНОЕ МЕНЮ

# ================================================================

def show_menu(chat_id, message_id=None):
markup = InlineKeyboardMarkup()
markup.add(InlineKeyboardButton(“📊 Моя подписка”,   callback_data=“check”))
markup.add(InlineKeyboardButton(“🎥 Тестовое видео”, callback_data=“trial”))
markup.add(InlineKeyboardButton(“💰 Тарифы”,         callback_data=“tariffs”))

```
text = "📱 <b>Главное меню</b>\n\nВыбери нужный раздел:"

if message_id:
    try:
        bot.edit_message_text(
            text, chat_id, message_id,
            reply_markup=markup, parse_mode="HTML"
        )
    except Exception:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
else:
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

# ТЕСТОВОЕ ВИДЕО

# ================================================================

@bot.callback_query_handler(func=lambda c: c.data == “trial”)
def cb_trial(call):
answer(call)
safe_edit(
call,
“🎥 <b>Тестовое видео</b>\n\n”
“Вот пример нашего контента:\n”
“👉 https://t.me/…”,   # ← замени на свою ссылку
make_back_btn(),
)

# ================================================================

# СПИСОК ТАРИФОВ

# ================================================================

def show_tariffs(chat_id, message_id=None):
markup = InlineKeyboardMarkup()
for k, v in PLANS.items():
markup.add(InlineKeyboardButton(
f”{v[‘title’]} — {v[‘days’]} дн. / {v[‘price’]}₽”,
callback_data=f”plan_{k}”,
))
markup.add(InlineKeyboardButton(“⬅ Назад”, callback_data=“menu”))

```
text = "💰 <b>Выбери тариф</b>"

if message_id:
    try:
        bot.edit_message_text(
            text, chat_id, message_id,
            reply_markup=markup, parse_mode="HTML"
        )
    except Exception:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
else:
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
```

@bot.callback_query_handler(func=lambda c: c.data == “tariffs”)
def cb_tariffs(call):
answer(call)
show_tariffs(call.message.chat.id, call.message.message_id)

# ================================================================

# ВЫБОР ТАРИФА → СПОСОБ ОПЛАТЫ

# ================================================================

@bot.callback_query_handler(func=lambda c: c.data.startswith(“plan_”))
def cb_plan(call):
answer(call)
uid = call.from_user.id
key = call.data[5:]   # убираем “plan_”

```
if key not in PLANS:
    return

user_state[uid] = key
p = PLANS[key]

markup = InlineKeyboardMarkup()
markup.add(InlineKeyboardButton("💳 Карта",  callback_data=f"pay_card_{key}"))
markup.add(InlineKeyboardButton("💰 USDT",   callback_data=f"pay_usdt_{key}"))
markup.add(InlineKeyboardButton("🚀 Boosty", callback_data=f"pay_boosty_{key}"))
markup.add(InlineKeyboardButton("⬅ Назад",  callback_data="tariffs"))

safe_edit(
    call,
    f"🔥 <b>{p['title']}</b>\n"
    f"📅 {p['days']} дн.\n"
    f"💸 {p['price']}₽\n\n"
    f"Выбери способ оплаты:",
    markup,
)
```

# ================================================================

# ЭКРАН ОПЛАТЫ

# ================================================================

@bot.callback_query_handler(func=lambda c: c.data.startswith(“pay_”))
def cb_pay(call):
answer(call)
uid  = call.from_user.id

```
# анти-спам
if uid in pending_payments:
    answer(call, "⚠️ Заявка уже отправлена, ожидай подтверждения")
    return

parts  = call.data.split("_")   # ["pay", "card"/"usdt"/"boosty", key]
method = parts[1]
key    = parts[2]

if key not in PLANS:
    return

user_state[uid] = key

markup = InlineKeyboardMarkup()
markup.add(InlineKeyboardButton("✅ Я оплатил",  callback_data="paid"))
markup.add(InlineKeyboardButton("⬅ Назад",       callback_data=f"plan_{key}"))

if method == "usdt":
    text = (
        f"💰 <b>Оплата USDT</b>\n\n"
        f"Отправь ровно <b>{PLANS[key]['price']}₽</b> эквивалент в USDT на адрес:\n\n"
        f"<code>{USDT_WALLET}</code>\n\n"
        f"После оплаты нажми ✅ Я оплатил"
    )
elif method == "card":
    text = (
        f"💳 <b>Оплата картой</b>\n\n"
        f"Переведи <b>{PLANS[key]['price']}₽</b> на карту:\n\n"
        f"<code>{CARD_NUMBER}</code>\n\n"
        f"После оплаты нажми ✅ Я оплатил"
    )
else:  # boosty
    text = (
        f"🚀 <b>Оплата через Boosty</b>\n\n"
        f"Перейди на страницу и оформи подписку:\n"
        f"👉 https://boosty.to/...\n\n"   # ← замени на свою ссылку
        f"После оплаты нажми ✅ Я оплатил"
    )

safe_edit(call, text, markup)
```

# ================================================================

# ПОЛЬЗОВАТЕЛЬ НАЖАЛ “Я ОПЛАТИЛ”

# ================================================================

@bot.callback_query_handler(func=lambda c: c.data == “paid”)
def cb_paid(call):
uid      = call.from_user.id
plan_key = user_state.get(uid)

```
if not plan_key:
    answer(call, "Ошибка: сначала выбери тариф")
    return

if uid in pending_payments:
    answer(call, "⚠️ Заявка уже отправлена")
    return

pending_payments[uid] = plan_key

# меняем кнопки у пользователя
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

# уведомление админу
admin_markup = InlineKeyboardMarkup()
admin_markup.add(InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_{uid}"))
admin_markup.add(InlineKeyboardButton("❌ Отклонить",   callback_data=f"reject_{uid}"))

p = PLANS[plan_key]
username = call.from_user.username or "нет"

bot.send_message(
    ADMIN_ID,
    f"💰 <b>Новая оплата!</b>\n\n"
    f"👤 ID: <code>{uid}</code>\n"
    f"👤 Username: @{username}\n"
    f"📦 Тариф: {p['title']} ({p['days']} дн.) — {p['price']}₽",
    reply_markup=admin_markup,
    parse_mode="HTML",
)

answer(call, "✅ Заявка отправлена")
```

# ================================================================

# КНОПКА “WAIT” — просто убираем крутилку

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

plan_key = pending_payments.pop(uid)
plan     = PLANS[plan_key]
expire   = datetime.now() + timedelta(days=plan["days"])

subs[uid] = {"expire": expire, "plan": plan_key}

# создаём одноразовую ссылку
try:
    invite = bot.create_chat_invite_link(
        chat_id=CHANNEL_ID,
        member_limit=1,
        expire_date=int(expire.timestamp()),   # ссылка тоже истекает
    )
    invite_url = invite.invite_link
except Exception as e:
    print("Ошибка создания ссылки:", e)
    invite_url = None

if invite_url:
    user_markup = InlineKeyboardMarkup()
    user_markup.add(InlineKeyboardButton("🚀 Войти в канал", url=invite_url))
    bot.send_message(
        uid,
        f"✅ <b>Оплата подтверждена!</b>\n\n"
        f"📦 Тариф: {plan['title']}\n"
        f"📅 Действует до: {expire.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"Нажми кнопку ниже чтобы войти в канал:",
        reply_markup=user_markup,
        parse_mode="HTML",
    )
else:
    bot.send_message(
        uid,
        f"✅ <b>Оплата подтверждена!</b>\n\n"
        f"📦 Тариф: {plan['title']}\n"
        f"📅 Действует до: {expire.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"Ссылку пришлёт администратор отдельно.",
        parse_mode="HTML",
    )

# обновляем сообщение у админа
bot.edit_message_text(
    f"✅ <b>ОДОБРЕНО</b>\nUser: <code>{uid}</code>\nТариф: {plan['title']}",
    call.message.chat.id,
    call.message.message_id,
    parse_mode="HTML",
)

answer(call, "Готово!")
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

bot.send_message(
    uid,
    "❌ <b>Оплата не подтверждена</b>\n\n"
    "Обратись к администратору если считаешь это ошибкой.",
    parse_mode="HTML",
)

bot.edit_message_text(
    f"❌ <b>ОТКЛОНЕНО</b>\nUser: <code>{uid}</code>",
    call.message.chat.id,
    call.message.message_id,
    parse_mode="HTML",
)

answer(call, "Отклонено")
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
if not sub:
    text = "❌ <b>Подписка не найдена</b>\n\nПерейди в тарифы чтобы оформить."
else:
    remaining = sub["expire"] - datetime.now()
    days      = remaining.days
    hours     = remaining.seconds // 3600

    if remaining.total_seconds() <= 0:
        text = "⏰ <b>Подписка истекла</b>\n\nПерейди в тарифы чтобы продлить."
    else:
        p    = PLANS[sub["plan"]]
        text = (
            f"✅ <b>Подписка активна</b>\n\n"
            f"📦 Тариф: {p['title']}\n"
            f"⏳ Осталось: {days} дн. {hours} ч.\n"
            f"📅 До: {sub['expire'].strftime('%d.%m.%Y %H:%M')}"
        )

safe_edit(call, text, make_back_btn())
```

# ================================================================

# ФОНОВЫЙ ПОТОК: АВТОВЫКИДЫВАНИЕ ИЗ КАНАЛА

# ================================================================

def kick_expired_users():
“”“Каждые 10 минут проверяет подписки и выкидывает истёкших”””
while True:
now     = datetime.now()
expired = [uid for uid, s in list(subs.items()) if s[“expire”] <= now]

```
    for uid in expired:
        try:
            bot.ban_chat_member(CHANNEL_ID, uid)      # кикаем
            bot.unban_chat_member(CHANNEL_ID, uid)    # снимаем бан (чтобы мог вернуться)
            bot.send_message(
                uid,
                "⏰ <b>Подписка истекла</b>\n\n"
                "Ты был удалён из канала.\n"
                "Перейди в /start чтобы продлить.",
                parse_mode="HTML",
            )
            print(f"Kicked expired user: {uid}")
        except Exception as e:
            print(f"Kick error for {uid}:", e)
        finally:
            subs.pop(uid, None)   # удаляем из базы в любом случае

    time.sleep(600)   # проверка каждые 10 минут
```

# Запускаем фоновый поток

kick_thread = threading.Thread(target=kick_expired_users, daemon=True)
kick_thread.start()

# ================================================================

# ЗАПУСК

# ================================================================

print(“✅ BOT STARTED”)
bot.infinity_polling(skip_pending=True)