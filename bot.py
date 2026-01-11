import telebot
import re
import os

# ---------------- CONFIG ----------------
BOT_TOKEN = "8526885322:AAHXqHDHWgFA9hpLPYl6inw8ftfVxZKNrV8"
MAIN_ADMIN_ID = 7247645931
CHANNEL_ID = -1003354190829
ESCROW_TAG = "@RYZEN_ESCROW"

bot = telebot.TeleBot(BOT_TOKEN)
deals = {}

# ---------------- DEAL ID FILE SYSTEM ----------------
DEAL_ID_FILE = "last_deal_id.txt"

def get_next_deal_id():
    if not os.path.exists(DEAL_ID_FILE):
        with open(DEAL_ID_FILE, "w") as f:
            f.write("1000")

    with open(DEAL_ID_FILE, "r") as f:
        last_id = int(f.read().strip())

    new_id = last_id + 1

    with open(DEAL_ID_FILE, "w") as f:
        f.write(str(new_id))

    return str(new_id)

# ---------------- CHECK GROUP ADMIN ----------------
def is_group_admin(chat_id, user_id):
    try:
        admins = bot.get_chat_administrators(chat_id)
        return any(admin.user.id == user_id for admin in admins)
    except:
        return False

# ---------------- /start ----------------
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "==============================\n"
        "WELCOME TO RYZEN ESCROW BOT\n"
        "==============================\n"
        "ALWAYS TRUSTED AND SAFE DEALS\n\n"
        "OWNER - @RYZEN_HEREE\n"
        "MAIN ESCROW - @RYZEN_ESCROW\n"
        "PROOFS - @RYZEN_ESCROW_DEALS\n"
        "VERIFIED ESCROWER - @RYZEN_ESCROWERS\n"
        "=============================="
    )

# ---------------- /add ----------------
@bot.message_handler(commands=['add'])
def add_deal(message):
    if not (message.from_user.id == MAIN_ADMIN_ID or is_group_admin(message.chat.id, message.from_user.id)):
        return

    if not message.reply_to_message:
        bot.reply_to(message, "Reply to deal form and use:\n/add <amount> <payment>")
        return

    text = message.reply_to_message.text

    buyer = re.search(r'Buyer Username\s*:-\s*@(\w+)', text)
    seller = re.search(r'Seller Username\s*:-\s*@(\w+)', text)
    details = re.search(r'Deal Details\s*:-\s*([\s\S]+)', text)

    if not buyer or not seller:
        bot.reply_to(message, "Buyer or Seller username missing.")
        return

    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "Usage: /add <amount> <payment>")
        return

    amount = args[1]
    payment = args[2]
    deal_id = get_next_deal_id()
    escrower = message.from_user.username or "ADMIN"

    deals[deal_id] = {
        "buyer": buyer.group(1),
        "seller": seller.group(1),
        "details": details.group(1).strip() if details else "N/A",
        "amount": amount,
        "payment": payment,
        "status": "ACTIVE",
        "escrower": escrower
    }

    bot.send_message(
        message.chat.id,
        f"PAYMENT RECEIVED\n\n"
        f"Deal ID: {deal_id}\n"
        f"Buyer: @{buyer.group(1)}\n"
        f"Seller: @{seller.group(1)}\n\n"
        f"Deal Details:\n{deals[deal_id]['details']}\n\n"
        f"Amount: {amount}\n"
        f"Payment: {payment}\n\n"
        f"Escrower: @{escrower}\n"
        f"Status: ACTIVE\n\n"
        f"Continue your deal\n"
        f"Escrow By: {ESCROW_TAG}"
    )

# ---------------- /done ----------------
@bot.message_handler(commands=['done'])
def done_deal(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /done <deal_id>")
        return

    deal_id = args[1]
    if deal_id not in deals:
        bot.reply_to(message, "Deal not found.")
        return

    deals[deal_id]["status"] = "DONE"
    d = deals[deal_id]

    text = (
        f"DEAL RELEASE DONE\n\n"
        f"Deal ID: {deal_id}\n"
        f"Buyer: @{d['buyer']}\n"
        f"Seller: @{d['seller']}\n"
        f"Amount: {d['amount']}\n"
        f"Escrower: @{d['escrower']}\n"
        f"Status: DONE"
    )

    bot.send_message(message.chat.id, text)
    bot.send_message(CHANNEL_ID, text)

# ---------------- /close ----------------
@bot.message_handler(commands=['close'])
def close_deal(message):
    if not (message.from_user.id == MAIN_ADMIN_ID or is_group_admin(message.chat.id, message.from_user.id)):
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /close <deal_id>")
        return

    deal_id = args[1]
    if deal_id not in deals:
        bot.reply_to(message, "Deal not found.")
        return

    deals[deal_id]["status"] = "CLOSED"
    d = deals[deal_id]

    text = (
        f"DEAL REFUND DONE\n\n"
        f"Deal ID: {deal_id}\n"
        f"Buyer: @{d['buyer']}\n"
        f"Seller: @{d['seller']}\n"
        f"Amount: {d['amount']}\n"
        f"Escrower: @{d['escrower']}\n"
        f"Status: CLOSED"
    )

    bot.send_message(message.chat.id, text)
    bot.send_message(CHANNEL_ID, text)

# ---------------- /check ----------------
@bot.message_handler(commands=['check'])
def check_deal(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /check <deal_id>")
        return

    deal_id = args[1]
    if deal_id not in deals:
        bot.reply_to(message, "Deal not found.")
        return

    d = deals[deal_id]
    bot.reply_to(
        message,
        f"Deal ID: {deal_id}\n"
        f"Buyer: @{d['buyer']}\n"
        f"Seller: @{d['seller']}\n"
        f"Amount: {d['amount']}\n"
        f"Payment: {d['payment']}\n"
        f"Escrower: @{d['escrower']}\n"
        f"Status: {d['status']}"
    )

# ---------------- /all ----------------
@bot.message_handler(commands=['all'])
def all_pending(message):
    if not (message.from_user.id == MAIN_ADMIN_ID or is_group_admin(message.chat.id, message.from_user.id)):
        return

    text = "PENDING DEALS\n\n"
    found = False

    for did, d in deals.items():
        if d["status"] == "ACTIVE":
            found = True
            text += f"{did} | @{d['buyer']} -> @{d['seller']} | {d['amount']}\n"

    if not found:
        text = "No pending deals."

    bot.reply_to(message, text)

# ---------------- /deal_history ----------------
@bot.message_handler(commands=['deal_history'])
def deal_history(message):
    if message.from_user.id != MAIN_ADMIN_ID:
        return

    text = "DEAL HISTORY\n\n"
    for did, d in deals.items():
        text += f"{did} | @{d['buyer']} -> @{d['seller']} | {d['amount']} | {d['status']}\n"

    bot.reply_to(message, text)

# ---------------- RUN ----------------
print("RYZEN ESCROW BOT RUNNING...")
bot.infinity_polling()
