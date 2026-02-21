import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import pyarabic.araby as araby

# ضع التوكن الخاص بك هنا
TOKEN = os.getenv('BOT_TOKEN')

# إعداد السجلات (Logs) لمراقبة عمل البوت
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_msg = (
        f" اهلاً بك يا {user_name} في بوت **حبر الأمة** للزخرفة الفاخرة ✨\n\n"
        "• أرسل الآن الاسم أو النص الذي تريد زخرفته."
    )
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # تنظيف النص من أي تشكيل قديم لضمان جودة الزخرفة الجديدة
    clean_text = araby.strip_tashkeel(user_text)
    
    # تخزين النص في بيانات المستخدم المؤقتة لاستخدامه عند الضغط على الأزرار
    context.user_data['current_text'] = clean_text

    # إنشاء الأزرار لاختيار النمط
    keyboard = [
        [InlineKeyboardButton("نمط الكشيدة (ممتد)", callback_data='style_1')],
        [InlineKeyboardButton("نمط الثلث المطور", callback_data='style_2')],
        [InlineKeyboardButton("نمط الزخرفة الملكية", callback_data='style_3')],
        [InlineKeyboardButton("نمط الأقواس الفخمة", callback_data='style_4')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("اختر نمط الزخرفة الذي تفضله:", reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = context.user_data.get('current_text', 'حبر الأمة')
    choice = query.data
    
    decorated = ""
    if choice == 'style_1':
        decorated = f"★ {text.replace(' ', 'ــــــــ')} ★"
    elif choice == 'style_2':
        # محاكاة لنمط الصورة بتشكيل مكثف
        decorated = f"★ {text} ★".translate(str.maketrans(" ", "ـ")) # إضافة كشيدة بسيطة
    elif choice == 'style_3':
        decorated = f"♛ {text} ♛"
    elif choice == 'style_4':
        decorated = f"『 {text} 』"

    response = (
        "✨ **تمت الزخرفة بنجاح!**\n"
        "اضغط على النص أدناه لنسخه:\n\n"
        f"`{decorated}`"
    )
    
    await query.edit_message_text(text=response, parse_mode='MarkdownV2')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("البوت يعمل الآن بكفاءة عالية...")
    app.run_polling()