import os
import json
import cv2
import numpy as np
import telebot
from telebot import types

# ==================== إعدادات البوت الجديد ====================
API_TOKEN = '8518065499:AAHavGhrg_FqNjkoV6wmxame-KP0hxEhmU4'
bot = telebot.TeleBot(API_TOKEN)

# إعدادات Adsgram
ADSGRAM_BLOCK_ID = "55679"

DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

USERS_FILE = 'users.json'

# --- إدارة قاعدة بيانات المستخدمين والعملات ---
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# ==================== أمر البدء والقائمة الرئيسية مع أزرار الميزات ====================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    users = load_users()
    user_id = str(message.from_user.id)
    args = message.text.split()
    
    # تسجيل مستخدم جديد مع 300 عملة هدية
    if user_id not in users:
        users[user_id] = {
            "balance": 300,
            "referrals": 0
        }
        
        # نظام الإحالة (إذا دخل عبر رابط صديق)
        if len(args) > 1:
            referrer_id = args[1]
            if referrer_id in users and referrer_id != user_id:
                users[referrer_id]["balance"] += 50  # مكافأة 50 عملة للمُحيل
                try:
                    bot.send_message(int(referrer_id), "🎉 مبروك! لقد حصلت على 50 عملة لانضمام صديق عبر رابط إحالتك.")
                except:
                    pass
                    
        save_users(users)
        
    balance = users[user_id]["balance"]
    
    # تصميم أزرار الميزات والقائمة التفاعلية
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # أزرار الميزات الرئيسية
    btn_remove_wm = types.InlineKeyboardButton("🎬 إزالة علامة مائية", callback_data="feature_remove_wm")
    btn_tts = types.InlineKeyboardButton("🔊 تحويل نص إلى صوت", callback_data="feature_tts")
    btn_translate = types.InlineKeyboardButton("🌐 ترجمة فيديو", callback_data="feature_translate")
    
    # أزرار الحساب والأرباح
    btn_balance = types.InlineKeyboardButton("💰 رصيدي", callback_data="check_balance")
    btn_earn = types.InlineKeyboardButton("🎁 اربح عملات (Adsgram)", callback_data="earn_coins")
    
    # ترتيب الأزرار في القائمة
    markup.add(btn_remove_wm)
    markup.add(btn_tts, btn_translate)
    markup.add(btn_balance, btn_earn)
    
    welcome_text = (
        f"مرحباً بك في بوت الخدمات الذكية الشامل! 🚀\n\n"
        f"💳 رصيدك الحالي: **{balance} عملة**\n"
        f"⚠️ كل عملية معالجة تستهلك **10 عملات**.\n\n"
        f"اختر الميزة التي تريد استخدامها من الأزرار أدناه:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# ==================== التعامل مع الأزرار التفاعلية والميزات ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    users = load_users()
    user_id = str(call.from_user.id)
    
    if user_id not in users:
        users[user_id] = {"balance": 300, "referrals": 0}
        save_users(users)
        
    if call.data == "feature_remove_wm":
        bot.answer_callback_query(call.id, "أرسل لي الفيديو الآن لإزالة العلامة المائية!")
        bot.send_message(call.message.chat.id, "📥 يرجى إرسال الفيديو الذي تريد إزالة العلامة المائية منه:")
        
    elif call.data == "feature_tts":
        bot.answer_callback_query(call.id, "ميزة تحويل النص إلى صوت قيد التفعيل!")
        bot.send_message(call.message.chat.id, "📝 أرسل النص الذي تريد تحويله إلى ملف صوتي:")
        
    elif call.data == "feature_translate":
        bot.answer_callback_query(call.id, "ميزة ترجمة الفيديوهات قريباً!")
        bot.send_message(call.message.chat.id, "🌐 ميزة ترجمة الفيديوهات ستتوفر في التحديث القادم إن شاء الله.")
        
    elif call.data == "check_balance":
        balance = users[user_id]["balance"]
        bot.answer_callback_query(call.id, f"رصيدك الحالي هو: {balance} عملة", show_alert=True)
        
    elif call.data == "earn_coins":
        bot_username = bot.get_me().username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        
        # لوحة أزرار للربح (إحالة + إعلانات Adsgram بمعرف 55679)
        earn_markup = types.InlineKeyboardMarkup(row_width=1)
        btn_ad = types.InlineKeyboardButton("📺 شاهد إعلان واكسب عملات (Adsgram)", callback_data="watch_ad")
        earn_markup.add(btn_ad)
        
        earn_text = (
            f"🎁 **طرق ربح العملات المجانية:**\n\n"
            f"1️⃣ **رابط الإحالة الخاص بك:**\nشارك هذا الرابط مع أصدقائك، واكسب **50 عملة** عن كل شخص يدخل البوت عبرك:\n`{ref_link}`\n\n"
            f"2️⃣ **مشاهدة الإعلانات:**\nاضغط على الزر أدناه لمشاهدة إعلان قصير عبر نظام Adsgram (Block ID: `{ADSGRAM_BLOCK_ID}`) وكسب مكافأتك!"
        )
        bot.send_message(call.message.chat.id, earn_text, reply_markup=earn_markup, parse_mode="Markdown")
        
    elif call.data == "watch_ad":
        users[user_id]["balance"] += 20  # مكافأة مشاهدة الإعلان
        save_users(users)
        new_bal = users[user_id]["balance"]
        bot.answer_callback_query(call.id, f"🎉 شكراً لمشاهدة الإعلان! تمت إضافة 20 عملة لرصيدك. رصيدك الحالي: {new_bal}", show_alert=True)
        
    elif call.data == "buy_coins":
        bot.send_message(call.message.chat.id, "🛒 لشراء باقات العملات، يرجى التواصل مع المطور.")

# ==================== معالجة الفيديوهات وإزالة العلامات ====================
@bot.message_handler(content_types=['video'])
def handle_video(message):
    users = load_users()
    user_id = str(message.from_user.id)
    
    if user_id not in users:
        users[user_id] = {"balance": 300, "referrals": 0}
        
    # التحقق من كفاية الرصيد
    if users[user_id]["balance"] < 10:
        bot.reply_to(message, "❌ رصيدك غير كافٍ! تحتاج إلى 10 عملات على الأقل لمعالجة الفيديو. اضغط على /start لربح عملات مجانية عبر الإعلانات أو الإحالات.")
        return
        
