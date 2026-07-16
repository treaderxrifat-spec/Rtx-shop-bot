import telebot
import pandas as pd
from openpyxl import load_workbook
import os
import threading
import http.server
import socketserver

# ১. টোকেন সেটআপ
# আপনার বটের সঠিক টোকেনটি এখানে দেওয়া আছে
BOT_TOKEN = "7950793132:AAEvTf9bU5K9k05rC4P6pZUX2QW"  
bot = telebot.TeleBot(BOT_TOKEN)

# এক্সেল ফাইলের নাম
EXCEL_FILE = "users.xlsx"

# ২. Excel ফাইল ইনিশিয়ালাইজ করা (ফাইল না থাকলে নতুন তৈরি করবে)
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["User ID", "Username", "First Name"])
    df.to_excel(EXCEL_FILE, index=False)

# ৩. /start কমান্ড হ্যান্ডলার (ইউজার আইডি সেভ এবং বাটন শো করা)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username if message.from_user.username else "N/A"
    first_name = message.from_user.first_name if message.from_user.first_name else "N/A"
    
    # ডেটা এক্সেল ফাইলে সেভ করার লজিক
    try:
        df = pd.read_excel(EXCEL_FILE)
        if user_id not in df["User ID"].values:
            new_row = pd.DataFrame([[user_id, username, first_name]], columns=["User ID", "Username", "First Name"])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(EXCEL_FILE, index=False)
    except Exception as e:
        print(f"Excel Error: {e}")

    # টেলিগ্রাম কাস্টম কীপ্যাড/বোতাম তৈরি
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("🛍️ Shop")
    btn2 = telebot.types.KeyboardButton("ℹ️ About Us")
    markup.add(btn1, btn2)
    
    bot.reply_to(message, f"স্বাগতম {first_name}! নিচে দেওয়া বাটনে ক্লিক করুন।", reply_markup=markup)

# ৪. টেক্সট মেসেজ হ্যান্ডলার (বাটন ক্লিকের রিপ্লাই)
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if message.text == "🛍️ Shop":
        bot.send_message(message.chat.id, "আমাদের শপ এখন ওপেন আছে! যেকোনো প্রোডাক্ট অর্ডার করতে ইনবক্স করুন।")
    elif message.text == "ℹ️ About Us":
        bot.send_message(message.chat.id, "আমরা নির্ভরযোগ্য এবং দ্রুত ডেলিভারি নিশ্চিত করি। আমাদের সাথে থাকার জন্য ধন্যবাদ!")

# =====================================================================
# 🛠️ RENDER PORT ERROR FIX (ডামি ওয়েব সার্ভার)
# =====================================================================
def run_dummy_server():
    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler
    # পোর্ট অলরেডি ব্লকেড থাকলে যাতে ক্র্যাশ না করে
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Dummy server running on port {PORT}")
        httpd.serve_forever()

# আলাদা থ্রেডে ওয়েব সার্ভার চালু করা, যাতে বট ব্যাকগ্রাউন্ডে নিরবচ্ছিন্নভাবে চলে
threading.Thread(target=run_dummy_server, daemon=True).start()

# ৫. বট পোলিং স্টার্ট
print("Bot is starting successfully...")
bot.infinity_polling()
