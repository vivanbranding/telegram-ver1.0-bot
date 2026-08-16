import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# تنظیم کلید API گوگل
genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
شما دستیار هوش مصنوعی برندینگ هستید.
شعار برند: "true north" (سمتِ درست).
تیم برندینگ: ویوان (Vivan).
مخاطب هدف: مدیران کسب‌وکار و کارآفرینان.
لحن: کاملاً روان، ساده، بسیار قابل فهم، صمیمی اما حرفه‌ای.
هدف: ایجاد حس نیاز و توجه به فرصت‌های همکاری با استراتژیست برند.
نکته مهم: در پاسخ‌ها و محتوا حتماً به نحوی به شعار "true north" یا مفهوم "سمتِ درست" اشاره کنید.
"""

# ساخت مدل با دسترسی استاندارد
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من دستیار هوش مصنوعی برندینگ هستم. چطور می‌توانم در مسیر پیدا کردن «سمتِ درست» (true north) کسب‌وکارتان به شما کمک کنم؟")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        response = model.generate_content(user_text)
        if response and response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("پاسخی دریافت نشد. لطفاً دوباره تلاش کنید.")
    except Exception as e:
        logging.error(f"Error generating content: {e}")
        # تست مدل جایگزین در صورت بروز خطا
        try:
            fallback_model = genai.GenerativeModel(
                model_name="gemini-2.5-pro",
                system_instruction=SYSTEM_INSTRUCTION
            )
            fallback_response = fallback_model.generate_content(user_text)
            await update.message.reply_text(fallback_response.text)
        except Exception as fallback_error:
            logging.error(f"Fallback error: {fallback_error}")
            await update.message.reply_text("متأسفانه مشکلی در ارتباط با سرور گوگل پیش آمده است. لطفاً کلید GEMINI_API_KEY خود را بررسی کنید.")

if __name__ == '__main__':
    proxy_url = "http://proxy.server:3128"
    
    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .proxy(proxy_url)
        .get_updates_proxy(proxy_url)
        .build()
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("ربات فعال شد...")
    app.run_polling()
