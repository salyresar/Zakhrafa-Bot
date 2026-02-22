import os
import logging
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

# 2. سيرفر الـ Keep-Alive للبقاء مستيقظاً على Render
flask_app = Flask('')
@flask_app.route('/')
def home(): return "Bot is Online!"

def run_flask(): 
    flask_app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# 3. محرك الزخرفة (8 أنماط احترافية)
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

# 4. معالجة الأوامر والرسائل
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>مرحباً بك في بوت زخرفة حبر الأمة 🖋️💎</b>\n\n"
        "أرسل الاسم أو النص الذي تريد زخرفته الآن.",
        parse_mode=ParseMode.HTML
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # تنظيف النص وحفظه
    text = araby.strip_tashkeel(update.message.text)
    context.user_data['active_text'] = text
    
    keyboard = [
        [InlineKeyboardButton("زخرفة إسلامية ۞", callback_data='style_islamic'), InlineKeyboardButton("تشكيل كامل ✍️", callback_data='style_tashkeel')],
        [InlineKeyboardButton("نمط المصحف ﴿﴾", callback_data='style_quran'), InlineKeyboardButton("نمط النجوم ★", callback_data='style_stars')],
        [InlineKeyboardButton("كشيدة ممتدة", callback_data='style_1'), InlineKeyboardButton("الثلث المطور", callback_data='style_2')],
        [InlineKeyboardButton("الزخرفة الملكية", callback_data='style_3'), InlineKeyboardButton("الأقواس الفخمة", callback_data='style_4')]
    ]
    await update.message.reply_text("<b>اختر نمط الزخرفة:</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    original_text = context.user_data.get('active_text', "حبر الأمة")
    styles = get_all_styles(original_text)
    result = styles.get(query.data, "خطأ")
    
    await query.edit_message_text(
        text=f"✅ <b>النتيجة:</b>\n\n<code>{result}</code>\n\nاضغط على النص للنسخ.",
        parse_mode=ParseMode.HTML
    )

# 5. التشغيل
if __name__ == '__main__':
    keep_alive()
    if not TOKEN:
        logging.error("❌ BOT_TOKEN missing!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        app.add_handler(CallbackQueryHandler(callback_handler))
        logging.info("🚀 البوت انطلق بنجاح وبدون تعقيدات...")
        app.run_polling()
