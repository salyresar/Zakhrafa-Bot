import os
import logging
import random
import html  # المكتبة القياسية لتأمين النصوص
import pyarabic.araby as araby
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram.constants import ParseMode

# 1. إعداد السجلات (للمراقبة في Render Logs)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get('BOT_TOKEN')

# 2. دوال الزخرفة والتشكيل
def get_artistic_styles(text):
    """توليد أنماط زخرفة متنوعة معالجة برمجياً"""
    # تنظيف النص من أي وسوم HTML قد يدخلها المستخدم للتخريب
    text = html.escape(text)
    
    # أنماط التشكيل والنقوش
    tashkeel = ['َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ً', 'ٌ', 'ٍ', 'ٰ']
    quranic = ['ۗ', 'ۚ', 'ۘ', 'ۙ', 'ۜ', '۟', '۠', '۞']
    
    def apply_marks(t):
        res = ""
        for c in t:
            res += c
            if c != ' ':
                if random.random() > 0.4: res += random.choice(tashkeel)
                if random.random() > 0.8: res += random.choice(quranic)
        return res

    kashida = text.replace(' ', 'ــــــــ')
    artistic_text = apply_marks(text)

    return {
        's1': f"★ {kashida} ★",
        's2': f"『 {text} 』",
        's3': f"♛ {text} ♛",
        's4': f"【 {text} 】",
        's5': f"✨ {artistic_text} ✨",
        's6': f"꧁ {text} ꧂",
        's7': f"◈ {artistic_text} ◈",
        's8': f"☾ {text} ☽"
    }

# 3. معالجات الأوامر
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>مرحباً بك في بوت زخرفة حبر الأمة المطوّر 🖋️</b>\n\n"
        "أرسل الاسم الذي تريد زخرفته الآن وسأقوم بالواجب.",
        parse_mode=ParseMode.HTML
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    if len(user_input) > 60:
        await update.message.reply_text("⚠️ النص طويل جداً، أرسل نصاً قصيراً (أقل من 60 حرفاً).")
        return

    # تنظيف النص وتخزينه
    clean_text = araby.strip_tashkeel(user_input)
    context.user_data['active_text'] = clean_text

    keyboard = [
        [InlineKeyboardButton("كشيدة ــــ", callback_data='s1'), InlineKeyboardButton("أقواس 『』", callback_data='s2')],
        [InlineKeyboardButton("تاج ملكي ♛", callback_data='s3'), InlineKeyboardButton("إطار عريض 【】", callback_data='s4')],
        [InlineKeyboardButton("تشكيل فني ✨", callback_data='s5'), InlineKeyboardButton("نباتي ꧁꧂", callback_data='s6')],
        [InlineKeyboardButton("مخطوطة ◈", callback_data='s7'), InlineKeyboardButton("هلالي ☾☽", callback_data='s8')],
    ]
    
    await update.message.reply_text(
        f"<b>📝 النص المستلم:</b> {html.escape(clean_text)}\n"
        f"<i>اختر النمط المطلوب:</i>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # جلب النص من الذاكرة أو من الرسالة نفسها في حال إعادة تشغيل البوت
    text = context.user_data.get('active_text')
    if not text:
        try:
            # استخراج النص برمجياً من رسالة البوت السابقة
            text = query.message.text.split('\n')[0].replace('📝 النص المستلم: ', '')
        except:
            text = "حبر الأمة"

    styles = get_artistic_styles(text)
    decorated = styles.get(query.data, text)

    # التنسيق النهائي باستخدام HTML
    # كود <code> يتيح النسخ عند اللمس في تلجرام
    response_html = (
        f"<b>✅ تمت الزخرفة بنجاح</b>\n\n"
        f"اضغط على النص أدناه للنسخ:\n"
        f"<code>{decorated}</code>"
    )

    try:
        await query.edit_message_text(text=response_html, parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(f"Error in editing: {e}")
        # في حال فشل التعديل، نرسل النتيجة في رسالة جديدة
        await query.message.reply_text(f"إليك النتيجة:\n<code>{decorated}</code>", parse_mode=ParseMode.HTML)

# 4. تشغيل البوت
if __name__ == '__main__':
    if not TOKEN:
        print("❌ خطأ: لم يتم ضبط BOT_TOKEN في إعدادات البيئة (Variables)!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        
        app.add_handler(CommandHandler('start', start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
        app.add_handler(CallbackQueryHandler(handle_callback))
        
        print("🚀 البوت يعمل الآن بنظام HTML المستقر...")
        app.run_polling()
