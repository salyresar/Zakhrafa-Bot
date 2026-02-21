import os
import logging
import random
import pyarabic.araby as araby
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram.helpers import escape_markdown

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get('BOT_TOKEN')

def apply_advanced_artistic(text):
    tashkeel_marks = ['َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ً', 'ٌ', 'ٍ']
    quranic_marks = ['ۗ', 'ۚ', 'ۘ', 'ۙ', 'ۜ', '۟', '۠', 'ٰ']
    result = ""
    for char in text:
        result += char
        if char != ' ':
            if random.random() > 0.5: result += random.choice(tashkeel_marks)
            if random.random() > 0.85: result += random.choice(quranic_marks)
    return result

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
    # استخدام Markdown عادي للترحيب لسهولة التنسيق
    await update.message.reply_text(
        "✨ *مرحباً بك في بوت زخرفة حبر الأمة* ✨\n\n"
        "أرسل الاسم أو العبارة التي تريد زخرفتها الآن.",
        parse_mode='Markdown'
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text
    # حماية ضد النصوص الطويلة جداً التي قد تعطل التنسيق
    if len(raw_text) > 50:
        await update.message.reply_text("⚠️ النص طويل جداً، يرجى إرسال نص أقل من 50 حرفاً.")
        return

    clean_text = araby.strip_tashkeel(raw_text)
    context.user_data['text'] = clean_text
    
    keyboard = [
        [InlineKeyboardButton("كشيدة ــــ", callback_data='s1'), InlineKeyboardButton("أقواس 『』", callback_data='s2')],
        [InlineKeyboardButton("تاج ملكي ♛", callback_data='s3'), InlineKeyboardButton("إطار عريض 【】", callback_data='s4')],
        [InlineKeyboardButton("تشكيل قرآني ✨", callback_data='s6'), InlineKeyboardButton("نقاط •—", callback_data='s5')],
        [InlineKeyboardButton("زهرة ✿", callback_data='s7'), InlineKeyboardButton("مخطوطة ◈", callback_data='s8')],
        [InlineKeyboardButton("نباتية ꧁", callback_data='s9'), InlineKeyboardButton("هلال ☾", callback_data='s10')],
    ]
    
    await update.message.reply_text(
        f"📝 النص: {clean_text}\n👇 اختر نمط الزخرفة:", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() 
    
    # حل مشكلة ضياع النص عند إعادة تشغيل السيرفر
    text = context.user_data.get('text')
    if not text:
        # محاولة استخراج النص من الرسالة السابقة إذا ضاع من الذاكرة
        try:
            text = query.message.text.split('\n')[0].replace('📝 النص: ', '')
        except:
            text = "حبر الأمة"

    styles = generate_styles(text)
    res = styles.get(query.data, text)
    
    # في MarkdownV2، داخل الـ Code Block (الذي يبدأ بـ `) 
    # نحتاج فقط لتشفير الـ backtick نفسه والـ backslash
    safe_res = res.replace('\\', '\\\\').replace('`', '\\`')
    
    # بناء الرسالة النهائية بتنسيق MarkdownV2 صحيح
    # الرموز مثل . - ! يجب تشفيرها خارج الـ code block
    response_text = (
        f"✅ *تمت الزخرفة بنجاح*\n\n"
        f"اضغط للنسخ:\n"
        f"\\[`{safe_res}`\\]" 
    )
    
    try:
        await query.edit_message_text(text=response_text, parse_mode='MarkdownV2')
    except Exception as e:
        logging.error(f"Final Error: {e}")
        # إذا فشل كل شيء، أرسل النص الخام
        await query.edit_message_text(text=f"إليك الزخرفة:\n\n{res}")

if __name__ == '__main__':
    if not TOKEN:
        print("Error: NO TOKEN FOUND")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
        app.add_handler(CallbackQueryHandler(button))
        app.run_polling()
