import os
import logging
import sqlite3
import random
import html
from threading import Thread
from flask import Flask
import pyarabic.araby as araby
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram.constants import ParseMode

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = 7271805464  # تأكد أن هذا هو معرفك الصحيح

# --- قسم قاعدة البيانات (لحفظ الأعضاء للإذاعة) ---
DB_FILE = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

init_db()

# --- سيرفر Flask ---
flask_app = Flask('')
@flask_app.route('/')
def home(): return "Bot is Online!"
def run_flask(): flask_app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run_flask).start()

# --- محرك الزخرفة ---
def get_all_styles(text):
    text = html.escape(text)
    tashkeel_list = ['َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ً', 'ٌ', 'ٍ', 'ٰ']
    def decorate(t, density=0.5):
        return "".join([c + random.choice(tashkeel_list) if c != ' ' and random.random() < density else c for c in t])
    return {
        'style_islamic': f"۞ {decorate(text, 0.4)} ۞",
        'style_tashkeel': f"{decorate(text, 0.9)}",
        'style_quran': f"﴿ {text} ﴾",
        'style_stars': f"★彡 {text} 彡★",
        'style_1': f"{text.replace('', 'ـ')[1:-1]}", 
        'style_2': f"✨ {decorate(text, 0.7)} ✨", 
        'style_3': f"👑 ⚜️ {text} ⚜️ 👑", 
        'style_4': f"⟦ {text} ⟧"
    }

# --- الأوامر الجديدة (الإذاعة والإحصائيات) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id) # حفظ المستخدم عند الضغط على start
    await update.message.reply_text("<b>مرحباً بك في بوت زخرفة حبر الأمة 🖋️</b>\nأرسل النص الآن.", parse_mode=ParseMode.HTML)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    users = get_all_users()
    await update.message.reply_text(f"📊 عدد المشتركين في قاعدة البيانات: {len(users)}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    # التأكد من وجود نص للإذاعة
    if not context.args:
        await update.message.reply_text("❌ يرجى كتابة الرسالة بعد الأمر. مثال:\n`/broadcast السلام عليكم`", parse_mode=ParseMode.Markdown)
        return

    broadcast_msg = " ".join(context.args)
    users = get_all_users()
    success, fail = 0, 0
    
    await update.message.reply_text(f"⏳ جاري بدء الإذاعة لـ {len(users)} مستخدم...")
    
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=broadcast_msg)
            success += 1
        except Exception:
            fail += 1
            
    await update.message.reply_text(f"✅ انتهت الإذاعة:\n\nتم بنجاح: {success}\nفشل (قاموا بحظر البوت): {fail}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id) # حفظ المستخدم عند إرسال أي رسالة
    context.user_data['active_text'] = araby.strip_tashkeel(update.message.text)
    keyboard = [
        [InlineKeyboardButton("زخرفة إسلامية ۞", callback_data='style_islamic'), InlineKeyboardButton("تشكيل كامل ✍️", callback_data='style_tashkeel')],
        [InlineKeyboardButton("نمط المصحف ﴿﴾", callback_data='style_quran'), InlineKeyboardButton("نمط النجوم ★", callback_data='style_stars')],
        [InlineKeyboardButton("كشيدة ممتدة", callback_data='style_1'), InlineKeyboardButton("الثلث المطور", callback_data='style_2')],
        [InlineKeyboardButton("الزخرفة الملكية", callback_data='style_3'), InlineKeyboardButton("الأقواس الفخمة", callback_data='style_4')]
    ]
    await update.message.reply_text("اختر النمط:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    styles = get_all_styles(context.user_data.get('active_text', "حبر الأمة"))
    result = styles.get(query.data, "خطأ")
    await query.edit_message_text(f"<code>{result}</code>", parse_mode=ParseMode.HTML)

if __name__ == '__main__':
    keep_alive()
    if TOKEN:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('stats', stats)) # أضفنا أمر الإحصائيات
        app.add_handler(CommandHandler('broadcast', broadcast)) # أضفنا أمر الإذاعة
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        app.add_handler(CallbackQueryHandler(callback_handler))
        app.run_polling()
