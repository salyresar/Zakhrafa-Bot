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

# 1. إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = 7271805464 

# 2. قاعدة البيانات (SQLite)
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

init_db()

# 3. سيرفر الـ Keep-Alive
flask_app = Flask('')
@flask_app.route('/')
def home(): return "Bot is Online!"
def run_flask(): flask_app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# 4. محرك الزخرفة الشامل (8 أنماط)
def get_all_styles(text):
    text = html.escape(text)
    tashkeel_list = ['َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ً', 'ٌ', 'ٍ', 'ٰ']
    islamic_marks = ['۞', '🕌', '📿', '🕋', '🌙']
    
    def decorate(t, density=0.5):
        res = ""
        for char in t:
            res += char
            if char != ' ' and random.random() < density:
                res += random.choice(tashkeel_list)
        return res

    return {
        # الأنماط السابقة
        'style_1': f"{text.replace('', 'ـ')[1:-1]}", 
        'style_2': f"✨ {decorate(text, 0.7)} ✨", 
        'style_3': f"👑 ⚜️ {text} ⚜️ 👑", 
        'style_4': f"⟦ {text} ⟧",
        # الأنماط الجديدة (إسلامية وتشكيل)
        'style_islamic': f"۞ {decorate(text, 0.4)} ۞",
        'style_tashkeel': f"{decorate(text, 0.9)}", # تشكيل كامل لكل الحروف
        'style_quran': f"﴿ {text} ﴾", # نمط المصحف
        'style_stars': f"★彡 {text} 彡★"
    }

# 5. الأوامر
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id)
    await update.message.reply_text("<b>أهلاً بك في بوت الزخرفة الإسلامية 🖋️</b>\nأرسل النص الآن لزخرفته.", parse_mode=ParseMode.HTML)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id)
    text = araby.strip_tashkeel(update.message.text)
    context.user_data['active_text'] = text
    
    keyboard = [
        [InlineKeyboardButton("زخرفة إسلامية ۞", callback_data='style_islamic'), InlineKeyboardButton("تشكيل كامل ✍️", callback_data='style_tashkeel')],
        [InlineKeyboardButton("نمط المصحف ﴿﴾", callback_data='style_quran'), InlineKeyboardButton("نمط النجوم ★", callback_data='style_stars')],
        [InlineKeyboardButton("كشيدة ممتدة", callback_data='style_1'), InlineKeyboardButton("الثلث المطور", callback_data='style_2')],
        [InlineKeyboardButton("الزخرفة الملكية", callback_data='style_3'), InlineKeyboardButton("الأقواس الفخمة", callback_data='style_4')]
    ]
    await update.message.reply_text("<b>اختر النمط الفاخر:</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    styles = get_all_styles(context.user_data.get('active_text', "حبر الأمة"))
    result = styles.get(query.data, "خطأ")
    await query.edit_message_text(f"✅ <b>النتيجة:</b>\n\n<code>{result}</code>\n\nاضغط للنسخ.", parse_mode=ParseMode.HTML)

if __name__ == '__main__':
    keep_alive()
    if TOKEN:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        app.add_handler(CallbackQueryHandler(callback_handler))
        logging.info("🚀 البوت يعمل الآن بـ 8 أنماط...")
        app.run_polling()
