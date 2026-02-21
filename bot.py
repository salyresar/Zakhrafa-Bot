import os
import logging
import random
import html
from threading import Thread
from flask import Flask
import pyarabic.araby as araby
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram.constants import ParseMode

# 1. الإعدادات وسجلات المراقبة
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get('BOT_TOKEN')
# ضع رابط المونجو دي بي الخاص بك هنا أو في Environment Variables
MONGO_URI = os.environ.get('MONGO_URI')
ADMIN_ID = 7271805464 # ضع معرفك الرقمي هنا

# 2. الاتصال بقاعدة بيانات MongoDB
client = MongoClient(MONGO_URI)
db = client['sample_mflix']
users_col = db['users']

def add_user(user_id):
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({"user_id": user_id})

# 3. سيرفر الـ Keep-Alive لإبقاء البوت مستيقظاً
flask_app = Flask('')
@flask_app.route('/')
def home(): return "Bot is Running!"

def run_flask(): flask_app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# 4. محرك الزخرفة الإسلامية والفنية
def get_islamic_styles(text):
    text = html.escape(text)
    tashkeel = ['َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ً', 'ٌ', 'ٍ', 'ٰ']
    quranic_marks = ['ۗ', 'ۚ', 'ۘ', 'ۙ', 'ۜ', '۟', '۠', '۞']
    
    def decorate(t, density=0.5):
        res = ""
        for char in t:
            res += char
            if char != ' ':
                if random.random() < density: res += random.choice(tashkeel)
                if random.random() < 0.15: res += random.choice(quranic_marks)
        return res

    return {
        'i1': f"۞ {decorate(text, 0.6)} ۞",
        'i2': f"꧁ {text} ꧂",
        'i3': f"☾ {decorate(text, 0.4)} ☽",
        'i4': f"◈ {text.replace(' ', ' ◈ ')} ◈",
        'i5': f"✨ {decorate(text, 0.7)} ✨",
        'i6': f"【 {text} 】"
    }

# 5. الأوامر البرمجية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id)
    await update.message.reply_text(
        "<b>أهلاً بك في نسخة 'حبر الأمة' الاحترافية 🖋️💎</b>\n\n"
        "أرسل الاسم أو النص المراد زخرفته بنقوش إسلامية وفنية.",
        parse_mode=ParseMode.HTML
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    count = users_col.count_documents({})
    await update.message.reply_text(f"📊 إجمالي عدد المشتركين الدائمين: <b>{count}</b>", parse_mode=ParseMode.HTML)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("❌ اكتب الرسالة بعد الأمر.")
        return
    
    users = users_col.find()
    s, f = 0, 0
    for user in users:
        try:
            await context.bot.send_message(chat_id=user['user_id'], text=msg)
            s += 1
        except: f += 1
    await update.message.reply_text(f"✅ تم بنجاح: {s}\n❌ فشل (حظر): {f}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id)
    text = araby.strip_tashkeel(update.message.text)
    context.user_data['t'] = text
    
    keyboard = [
        [InlineKeyboardButton("نقش إسلامي ۞", callback_data='i1'), InlineKeyboardButton("زخرفة نباتية ꧁", callback_data='i2')],
        [InlineKeyboardButton("نمط الهلال ☾", callback_data='i3'), InlineKeyboardButton("مخطوطة هندسية ◈", callback_data='i4')],
        [InlineKeyboardButton("تشكيل مكثف ✨", callback_data='i5'), InlineKeyboardButton("إطار فخم 【】", callback_data='i6')],
    ]
    await update.message.reply_text("اختر النمط الفاخر:", reply_markup=InlineKeyboardMarkup(keyboard))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = context.user_data.get('t', "حبر الأمة")
    styles = get_islamic_styles(text)
    result = styles.get(query.data, text)
    
    await query.edit_message_text(
        text=f"✅ <b>تمت الزخرفة بنجاح:</b>\n\n<code>{result}</code>\n\nاضغط على النص للنسخ.",
        parse_mode=ParseMode.HTML
    )

# 6. التشغيل
if __name__ == '__main__':
    keep_alive() # تشغيل السيرفر الموازي للـ Keep-Alive
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('stats', stats))
    app.add_handler(CommandHandler('broadcast', broadcast))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    app.run_polling()



