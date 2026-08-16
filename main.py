import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ساخت کلاینت جدید گوگل
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
شما دستیار هوش مصنوعی برندینگ هستید.
شعار برند: "true north" (سمتِ درست).
تیم برندینگ: ویوان (Vivan).
مخاطب هدف: مدیران کسب‌وکار و کارآفرینان.
لحن: کاملاً روان، ساده، بسیار قابل فهم، صمیمی اما حرفه‌ای.
هدف: ایجاد حس نیاز و توجه به فرصت‌های همکاری با استراتژیست برند.
نکته مهم: در پاسخ‌ها و محتوا حتماً به نحوی به شعار "true north" یا مفهوم "سمتِ درست" اشاره کنید.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من دستیار هوش مصنوعی برندینگ هستم. چطور می‌توانم در مسیر پیدا کردن «سمتِ درست» (true north) کسب‌وکارتان به شما کمک کنم؟")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        response = client.models.generate_content(
    model='gemini-1.5-pro',
    contents=user_text,
    config={'system_instruction': SYSTEM_INSTRUCTION}
)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("متأسفانه مشکلی در ارتباط با هوش مصنوعی پیش آمده است. لطفاً دوباره تلاش کنید.")

if __name__ == '__main__':
    # استفاده از پراکسی پیش‌فرض PythonAnywhere برای رفع خطای شبکه
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
