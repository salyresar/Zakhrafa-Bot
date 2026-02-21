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

# 1. إعداد السجلات (Logs)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = 7271805464  # معرفك الرقمي

# 2. إعداد قاعدة البيانات المحلية SQLite
DB_FILE = "users_data.db"

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

def get_users_count():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

# تشغيل تهيئة القاعدة
init_db()

# 3. سيرفر الـ Keep-Alive
flask_app = Flask('')
@flask_app.route('/')
def home(): return "Bot is Online!"

def run_flask(): 
    flask_app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# 4. محرك الزخرفة الإسلامية
def get_islamic_styles(text):
    text = html.escape(text)
    tashkeel = ['َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ً', 'ٌ', 'ٍ', 'ٰ']
    def decorate(t):
        res = ""
        for char in t:
            res += char
            if char != ' ' and random.random() < 0.4: res += random.choice(tashkeel)
        return res
    return {
        'i1': f"۞ {decorate(text)} ۞",
        'i2': f"꧁ {text} ꧂",
        'i3': f"☾ {decorate(text)} ☽",
        'i4': f"◈ {text.replace(' ', ' ◈ ')} ◈"
    }

# 5. معالجة الأوامر
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id)
    await update.message.reply_text(
        "<b>مرحباً بك في بوت زخرفة حبر الأمة 🖋️💎</b>\n\n"
        "أرسل الاسم أو النص الآن لزخرفته فوراً.",
        parse_mode=ParseMode.HTML
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    count = get_users_count()
    await update.message.reply_text(f"📊 عدد المشتركين الحاليين: <b>{count}</b>", parse_mode=ParseMode.HTML)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("❌ اكتب الرسالة بعد الأمر.")
        return
    users = get_all_users()
    s, f = 0, 0
    for u_id in users:
        try:
            await context.bot.send_message(chat_id=u_id, text=msg)
            s += 1
        except: f += 1
    await update.message.reply_text(f"✅ تم الإرسال لـ: {s}\n❌ فشل لـ: {f}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id)
    text = araby.strip_tashkeel(update.message.text)
    context.user_data['active_text'] = text
    keyboard = [
        [InlineKeyboardButton("نقش إسلامي ۞", callback_data='i1'), InlineKeyboardButton("زخرفة نباتية ꧁", callback_data='i2')],
        [InlineKeyboardButton("نمط الهلال ☾", callback_data='i3'), InlineKeyboardButton("مخطوطة هندسية ◈", callback_data='i4')],
    ]
    await update.message.reply_text("اختر نمط الزخرفة:", reply_markup=InlineKeyboardMarkup(keyboard))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    styles = get_islamic_styles(context.user_data.get('active_text', "حبر الأمة"))
    result = styles.get(query.data, "خطأ في المعالجة")
    await query.edit_message_text(f"✅ <b>النتيجة:</b>\n\n<code>{result}</code>", parse_mode=ParseMode.HTML)

# 6. التشغيل
if __name__ == '__main__':
    keep_alive()
    if not TOKEN:
        logging.error("❌ BOT_TOKEN missing in Render settings!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('stats', stats))
        app.add_handler(CommandHandler('broadcast', broadcast))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        app.add_handler(CallbackQueryHandler(callback_handler))
        logging.info("🚀 البوت يعمل بنظام SQLite السهل...")
        app.run_polling()
