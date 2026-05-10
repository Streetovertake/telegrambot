import telebot
import os
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ["TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
USDT_WALLET = os.environ["USDT_WALLET"]

bot = telebot.TeleBot(TOKEN)

subs = {}
pending_payments = {}
user_state = {}
nav_stack = {}

#___stack

def push(user_id, state):
    nav_stack.setdefault(user_id, []).append(state)

def pop(user_id):
    if user_id in nav_stack and nav_stack[user_id]:
        return nav_stack[user_id].pop()
    return None
    
#___plan

PLANS = {
    "basic": {"days": 1, "price": 600, "title": "Basic"},
    "middle": {"days": 7, "price": 1600, "title": "Middle"},
    "hot": {"days": 30, "price": 2500, "title": "HOT"},
    "ahhh": {"days": 30, "price": 4990, "title": "Ahhh"}
}

@bot.message_handler(commands=['start'])
def start(message):
    show_menu(message.chat.id)
    
    markup = InlineKeyboardMarkup()
    
    markup.add(InlineKeyboardButton("🎬 Тестовое видео", callback_data="trial_video"))
    markup.add(InlineKeyboardButton("💰 Список тарифов", callback_data="tariffs"))
    
#___

def back_to_plan(call):
    plan = user_state.get(call.from_user.id)

    if not plan:
        show_tariffs(call.message.chat.id, call.message.message_id)
        return

    show_plan(call, plan)
    
#___tariffs

def show_tariffs(chat_id, message_id=None, user_id=None):

    if user_id:
        push(user_id, "menu")

    markup = InlineKeyboardMarkup()

    for k, v in PLANS.items():
        markup.add(InlineKeyboardButton(
            f"{v['title']} / {v['price']}₽",
            callback_data=f"plan_{k}"
        ))

    text = "💰 <b>Выбери тариф</b>"

    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    
#___menu

def show_menu(chat_id, message_id=None):

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📊 Проверить подписку", callback_data="check_sub"))
    markup.add(InlineKeyboardButton("🎥 Тестовое видео", callback_data="trial"))
    markup.add(InlineKeyboardButton("💰 Список тарифов", callback_data="tariffs"))

    text = "📱 <b>МЕНЮ</b>"

    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")

#___plan

@bot.callback_query_handler(func=lambda call: call.data.startswith("plan_"))
def plan(call):

    user_id = call.from_user.id
    plan_key = call.data.split("_")[1]

    push(user_id, "tariffs")  # 👈 запоминаем, что пришли из списка тарифов

    show_plan(call, plan_key)

    plan_key = call.data.split("_")[1]

    if plan_key not in PLANS:
        return
    user_state[call.from_user.id] = plan_key

    plan = PLANS[plan_key]

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("USDT", callback_data=f"usdt_{plan_key}"))
    markup.add(InlineKeyboardButton("Card", callback_data=f"card_{plan_key}"))
    markup.add(InlineKeyboardButton("Boosty", callback_data=f"boosty_{plan_key}"))
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))
    
    bot.edit_message_text(
        f"{plan['title']} — {plan['price']}₽",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

#___showplan

def show_plan(call, plan_key):

    user_id = call.from_user.id
    push(user_id, f"plan_{plan_key}")

    plan = PLANS[plan_key]

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💳 Карта", callback_data=f"card_{plan_key}"))
    markup.add(InlineKeyboardButton("💰 USDT", callback_data=f"usdt_{plan_key}"))
    markup.add(InlineKeyboardButton("🚀 Boosty", callback_data=f"boosty_{plan_key}"))

    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))

    bot.edit_message_text(
        f"🔥 {plan['title']}\n💸 {plan['price']}₽",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode="HTML"
    )
    
#___back

@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):

    user_id = call.from_user.id
    prev = pop(user_id)

    # если история пустая — кидаем в меню
    if not prev:
        show_menu(call.message.chat.id, call.message.message_id)
        return

    # возврат по шагам
    if prev == "menu":
        show_menu(call.message.chat.id, call.message.message_id)

    elif prev == "tariffs":
        show_tariffs(call.message.chat.id, call.message.message_id)

    elif prev.startswith("plan_"):
        plan_key = prev.split("_")[1]
        show_plan(call, plan_key)

    else:
        show_tariffs(call.message.chat.id, call.message.message_id)
    
#___

@bot.callback_query_handler(func=lambda call: call.data.startswith("usdt_"))
def usdt(call):
    plan_key = call.data.split("_")[1]
    pay(call, "usdt", plan_key)

@bot.callback_query_handler(func=lambda call: call.data.startswith("card_"))
def card(call):
    plan_key = call.data.split("_")[1]
    pay(call, "card", plan_key)

@bot.callback_query_handler(func=lambda call: call.data.startswith("boosty_"))
def boosty(call):
    plan_key = call.data.split("_")[1]
    pay(call, "boosty", plan_key)
    
#___

@bot.callback_query_handler(func=lambda call: call.data.startswith("paid_"))
def paid(call):

    user_id = call.from_user.id
    plan_key = user_state.get(user_id)

    if not plan_key:
        bot.send_message(user_id, "Ошибка: выбери тариф заново")
        return

    pending_payments[user_id] = {
        "plan": plan_key,
        "method": "unknown"
    }

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Confirm", callback_data=f"confirm_{user_id}"))

    bot.send_message(
        ADMIN_ID,
        f"💰 PAYMENT\nUser: {user_id}\nPlan: {plan_key}",
        reply_markup=markup
    )

#___

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm(call):

    if call.from_user.id != ADMIN_ID:
        return

    user_id = int(call.data.split("_")[1])

    data = pending_payments.get(user_id)

    if not data:
        return

    plan_key = data["plan"]

    plan = PLANS[plan_key]

    subs[user_id] = {
        "expire": datetime.now() + timedelta(days=plan["days"]),
        "plan": plan_key
    }

    bot.send_message(user_id, "✅ Оплата подтверждена")
    bot.send_message(ADMIN_ID, f"Выдан план {plan_key}")

    pending_payments.pop(user_id, None)
    
#___

if __name__ == "__main__":
    print("🚀 BOT IS STARTING...")

    try:
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print("❌ BOT CRASHED:", e)