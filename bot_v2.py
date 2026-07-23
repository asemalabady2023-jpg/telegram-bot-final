import os
import logging
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def download_video(url):
    ydl_opts = {
        'format': 'best[filesize<50M]',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename, info.get('title', 'unknown')
    except Exception as e:
        return None, str(e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحباً! أرسل رابط فيديو 📥\n"
        "• YouTube\n• TikTok\n• Instagram\n• Twitter\n• Facebook"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith(('http://', 'https://')):
        await update.message.reply_text("❌ أرسل رابط صحيح")
        return
    
    wait_msg = await update.message.reply_text("⏳ جاري التحميل...")
    
    filename, title = download_video(url)
    
    if filename and os.path.exists(filename):
        await wait_msg.delete()
        with open(filename, 'rb') as f:
            await update.message.reply_video(f, caption=f"✅ {title}")
        os.remove(filename)
    else:
        await wait_msg.edit_text(f"❌ خطأ: {title}")

def main():
    if not TOKEN:
        return
    os.makedirs('downloads', exist_ok=True)
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
