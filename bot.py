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

PLANS = {
    "basic": {"days": 1, "price": 600, "title": "Basic"},
    "middle": {"days": 7, "price": 1600, "title": "Middle"},
    "hot": {"days": 30, "price": 2500, "title": "HOT"},
    "ahhh": {"days": 30, "price": 4990, "title": "Ahhh"}
}

@bot.message_handler(commands=['start'])
def start(message):
    show_tariffs(message.chat.id)
    
#___

def back_to_plan(call):
    plan = user_state.get(call.from_user.id)

    if not plan:
        show_tariffs(call.message.chat.id, call.message.message_id)
        return

    show_plan(call, plan)
    
#___

def show_tariffs(chat_id):
    markup = InlineKeyboardMarkup()

    for key, plan in PLANS.items():
        markup.add(InlineKeyboardButton(
            f"{plan['title']} / {plan['price']}₽",
            callback_data=f"plan_{key}"
        ))

    bot.send_message(chat_id, "Выбери тариф", reply_markup=markup)
    
#___

@bot.callback_query_handler(func=lambda call: call.data.startswith("plan_"))
def plan(call):

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

#___

@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    show_tariffs(call.message.chat.id)

def pay(call, method, plan_key):

    user_state[call.from_user.id] = plan_key

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))
    markup.add(InlineKeyboardButton("Я оплатил", callback_data=f"paid_{plan_key}_{method}"))

    if method == "usdt":
        text = f"USDT: {USDT_WALLET}"
    elif method == "card":
        text = "Card: 2202..."
    else:
        text = "Boosty link"

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )
    
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