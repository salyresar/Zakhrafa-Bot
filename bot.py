import os
import logging
import random
import html
import sqlite3 # لإدارة قاعدة البيانات
import pyarabic.araby as araby
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram.constants import ParseMode

# 1. الإعدادات الأساسية
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = 7271805464  # !!! استبدل هذا الرقم بـ ID حسابك على تلجرام !!!

# 2. إعداد قاعدة البيانات
db_conn = sqlite3.connect('bot_users.db', check_same_thread=False)
cursor = db_conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
db_conn.commit()

def add_user(user_id):
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    db_conn.commit()

def get_all_users():
    cursor.execute('SELECT user_id FROM users')
    return [row[0] for row in cursor.fetchall()]

# 3. دوال الزخرفة (نفس النسخة المستقرة السابقة)
def get_artistic_styles(text):
    text = html.escape(text)
    tashkeel = ['َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ً', 'ٌ', 'ٍ', 'ٰ']
    quranic = ['ۗ', 'ۚ', 'ۘ', 'ۙ', 'ۜ', '۟', '۠']
    
    def apply_marks(t):
        res = ""
        for c in t:
            res += c
            if c != ' ':
                if random.random() > 0.4: res += random.choice(tashkeel)
                if random.random() > 0.8: res += random.choice(quranic)
        return res

    return {
        's1': f"★ {text.replace(' ', 'ــــــــ')} ★",
        's2': f"『 {text} 』",
        's3': f"♛ {text} ♛",
        's4': f"✨ {apply_marks(text)} ✨",
        's5': f"꧁ {text} ꧂",
        's6': f"◈ {apply_marks(text)} ◈"
    }

# 4. الأوامر البرمجية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id) # إضافة المستخدم للقاعدة
    await update.message.reply_text(
        "<b>مرحباً بك في بوت زخرفة حبر الأمة المطوّر 🖋️</b>\n\n"
        "أرسل الاسم الذي تريد زخرفته الآن.",
        parse_mode=ParseMode.HTML
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض عدد الأعضاء (للمطور فقط)"""
    if update.effective_user.id != ADMIN_ID:
        return
    count = len(get_all_users())
    await update.message.reply_text(f"📊 عدد مستخدمي البوت حالياً: <b>{count}</b>", parse_mode=ParseMode.HTML)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال رسالة للجميع (للمطور فقط)"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    msg_to_send = " ".join(context.args)
    if not msg_to_send:
        await update.message.reply_text("❌ يرجى كتابة الرسالة بعد الأمر. مثال:\n`/broadcast أهلاً بالجميع`", parse_mode=ParseMode.HTML)
        return

    users = get_all_users()
    success, fail = 0, 0
    
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=msg_to_send)
            success += 1
        except:
            fail += 1
    
    await update.message.reply_text(f"✅ تم الإرسال إلى: {success}\n❌ فشل الإرسال إلى: {fail} (قاموا بحظر البوت)")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id) # تأكيد وجوده في القاعدة
    user_input = araby.strip_tashkeel(update.message.text)
    context.user_data['active_text'] = user_input

    keyboard = [
        [InlineKeyboardButton("كشيدة ــــ", callback_data='s1'), InlineKeyboardButton("أقواس 『』", callback_data='s2')],
        [InlineKeyboardButton("تاج ملكي ♛", callback_data='s3'), InlineKeyboardButton("تشكيل فني ✨", callback_data='s4')],
        [InlineKeyboardButton("نباتي ꧁꧂", callback_data='s5'), InlineKeyboardButton("مخطوطة ◈", callback_data='s6')],
    ]
    
    await update.message.reply_text(
        f"<b>📝 النص:</b> {html.escape(user_input)}\n<i>اختر النمط:</i>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = context.user_data.get('active_text', "حبر الأمة")
    styles = get_artistic_styles(text)
    decorated = styles.get(query.data, text)

    await query.edit_message_text(
        text=f"<b>✅ تمت الزخرفة</b>\n\n<code>{decorated}</code>",
        parse_mode=ParseMode.HTML
    )

# 5. تشغيل البوت
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('stats', stats))
    app.add_handler(CommandHandler('broadcast', broadcast))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    app.run_polling()
