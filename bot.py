import os
import logging
import random
import pyarabic.araby as araby
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram.helpers import escape_markdown

# إعداد السجلات لمتابعة العمل على سيرفر Render
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get('BOT_TOKEN')

# 1. دالة التشكيل الفني المتقدم (تشمل حركات ورموز قرآنية)
def apply_advanced_artistic(text):
    # الحركات الأساسية
    tashkeel_marks = ['َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ً', 'ٌ', 'ٍ']
    # الرموز القرآنية وعلامات الوقف لإعطاء فخامة
    quranic_marks = ['ۗ', 'ۚ', 'ۘ', 'ۙ', 'ۜ', '۟', '۠', 'ٰ', '۞']
    
    result = ""
    for char in text:
        result += char
        if char != ' ':
            # احتمالية إضافة حركة عادية (50%)
            if random.random() > 0.5:
                result += random.choice(tashkeel_marks)
            # احتمالية إضافة رمز قرآني نادر (15%) لزيادة الجمالية دون تشويه
            if random.random() > 0.85:
                result += random.choice(quranic_marks)
    return result

# 2. دالة توليد الأنماط المتعددة
def generate_styles(text):
    kashida = text.replace(' ', 'ــــــــ')
    artistic = apply_advanced_artistic(text)
    
    return {
        's1': f"★ {kashida} ★",
        's2': f"『 {text} 』",
        's3': f"♛ {text} ♛",
        's4': f"【 {text} 】",
        's5': f"•—「 {text} 」—•",
        's6': f"✨ {artistic} ✨",
        's7': f"~✿ {text} ✿~",
        's8': f"◈ {artistic} ◈",
        's9': f"꧁ {text} ꧂",
        's10': f"☾ {artistic} ☽"
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "✨ **مرحباً بك في بوت زخرفة حبر الأمة المطوّر** ✨\n\n"
        "أرسل الاسم أو العبارة التي تريد زخرفتها بنقوش فنية وقرآنية."
    )
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # تنظيف النص من أي تشكيل قديم لضمان جودة الزخرفة
    raw_text = update.message.text
    clean_text = araby.strip_tashkeel(raw_text)
    context.user_data['text'] = clean_text
    
    # توزيع الأزرار بشكل احترافي
    keyboard = [
        [InlineKeyboardButton("كشيدة ممتدة ــــ", callback_data='s1'), InlineKeyboardButton("أقواس فخمة 『』", callback_data='s2')],
        [InlineKeyboardButton("تاج ملكي ♛", callback_data='s3'), InlineKeyboardButton("إطار عريض 【】", callback_data='s4')],
        [InlineKeyboardButton("تشكيل قرآني ✨", callback_data='s6'), InlineKeyboardButton("نقاط متصلة •—", callback_data='s5')],
        [InlineKeyboardButton("زهرة الربيع ✿", callback_data='s7'), InlineKeyboardButton("مخطوطة هندسية ◈", callback_data='s8')],
        [InlineKeyboardButton("زخرفة نباتية ꧁", callback_data='s9'), InlineKeyboardButton("نمط الهلال ☾", callback_data='s10')],
    ]
    
    await update.message.reply_text(
        f"📝 النص المستلم: {clean_text}\n👇 اختر نمط الزخرفة والنقش:", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() 
    
    text = context.user_data.get('text', 'حبر الأمة')
    styles = generate_styles(text)
    res = styles.get(query.data, text)
    
    # تشفير النص ليعمل نظام "اضغط للنسخ" مع الرموز المعقدة
    safe_res = escape_markdown(res, version=2)
    response_text = f"✅ **تمت الزخرفة بنجاح**\n\nاضغط على النص أدناه لنسخه:\n\n`{safe_res}`"
    
    try:
        await query.edit_message_text(text=response_text, parse_mode='MarkdownV2')
    except Exception as e:
        logging.error(f"Markdown Error: {e}")
        await query.edit_message_text(text=f"إليك النتيجة:\n\n{res}\n\n(تم إرساله بدون ميزة النسخ السريع لتعقد الرموز)")

if __name__ == '__main__':
    if not TOKEN:
        print("Error: BOT_TOKEN not found!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
        app.add_handler(CallbackQueryHandler(button))
        print("البوت الاحترافي يعمل الآن...")
        app.run_polling()
