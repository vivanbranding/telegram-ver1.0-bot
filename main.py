import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai
from google.genai import types

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# تعریف کلاینت با SDK جدید گوگل
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
    response_text = None

    # استفاده از نام دقیق مدل‌های فعال در حساب شما همراه با پیشوند models/
    models_to_try = [
        'models/gemini-2.5-flash',
        'models/gemini-2.5-pro',
        'models/gemini-3.5-flash'
    ]

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_text,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION
                )
            )
            if response and response.text:
                response_text = response.text
                logging.info(f"پاسخ با موفقیت از مدل {model_name} دریافت شد.")
                break
        except Exception as e:
            logging.warning(f"تلاش برای مدل {model_name} با خطا مواجه شد: {e}")
            continue

    if response_text:
        await update.message.reply_text(response_text)
    else:
        await update.message.reply_text("متأسفانه مشکلی در پردازش پاسخ پیش آمده است. لطفاً دوباره پیام بفرستید.")

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
