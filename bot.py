import os
import shutil
import telebot
import instaloader
import yt_dlp
from telebot import types

# =====================================
# BOT TOKEN (Railway Variable)
# =====================================
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ BOT_TOKEN not found in Railway Variables")
    exit()

bot = telebot.TeleBot(TOKEN)

# =====================================
# INSTAGRAM LOADER
# =====================================
loader = instaloader.Instaloader(
    dirname_pattern="downloads",
    save_metadata=False,
    download_video_thumbnails=False,
    post_metadata_txt_pattern=""
)

# =====================================
# UI TEXTS
# =====================================
WELCOME_TEXT = """
╔════════════════════════╗
║    ⚡ KAMAL SYSTEM ⚡    ║
╚════════════════════════╝

🚀 Premium Downloader Bot

━━━━━━━━━━━━━━━━━━━━

🌍 MAXIMUM PUBLIC LINK SUPPORT

✅ Instagram Reels / Posts / Videos
✅ YouTube Videos / Shorts
✅ Facebook Public Videos
✅ Facebook Share Links (many cases)
✅ TikTok Public Videos
✅ Twitter / X Public Media
✅ Reddit Public Media
✅ Many Public Media Platforms

━━━━━━━━━━━━━━━━━━━━

⚡ Just Copy → Paste → Download
🎯 HD Output
🔥 Smart Download Engine
📦 Public Links Only

━━━━━━━━━━━━━━━━━━━━

👑 Powered by Kamall System 👑
📡 @KamallRoxzy
"""

COMPLETE_TEXT = """
╔════════════════════════╗
║   ⚡ READY FOR USE ⚡   ║
╚════════════════════════╝

⚡ Your File Is Successfully Delivered
🚀 Fast Process • Zero Delay
💎 Premium Output Activated

━━━━━━━━━━━━━━

🔁 Send Next Link
⚡ Ready For Next Download

━━━━━━━━━━━━━━

👑 Powered by Kamall System 👑
📡 @KamallRoxzy
"""

# =====================================
# BUTTONS
# =====================================
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🚀 Start Download")
    btn2 = types.KeyboardButton("📘 Help")
    markup.add(btn1)
    markup.add(btn2)
    return markup


# =====================================
# START
# =====================================
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        WELCOME_TEXT,
        reply_markup=main_keyboard()
    )


# =====================================
# HELP
# =====================================
@bot.message_handler(func=lambda m: m.text == "📘 Help")
def help_message(message):
    bot.reply_to(
        message,
        """
📘 HOW TO USE

Just send your public link.

Supported:
✅ Instagram
✅ YouTube
✅ Facebook
✅ TikTok
✅ Twitter / X
✅ Reddit

Private / protected content may fail.
"""
    )


# =====================================
# START BUTTON
# =====================================
@bot.message_handler(func=lambda m: m.text == "🚀 Start Download")
def ready_message(message):
    bot.reply_to(
        message,
        "⚡ Send your public media link now."
    )


# =====================================
# CLEAN DOWNLOADS
# =====================================
def clear_downloads():
    if os.path.exists("downloads"):
        try:
            shutil.rmtree("downloads")
        except:
            pass

    os.makedirs("downloads", exist_ok=True)


# =====================================
# SEND FILE
# =====================================
def send_downloaded_file(chat_id):
    for root, dirs, files in os.walk("downloads"):
        for file in files:
            if file.endswith((
                ".mp4",
                ".jpg",
                ".jpeg",
                ".png",
                ".webm",
                ".mkv"
            )):
                filepath = os.path.join(root, file)

                with open(filepath, "rb") as f:
                    if file.endswith((
                        ".mp4",
                        ".webm",
                        ".mkv"
                    )):
                        bot.send_video(
                            chat_id,
                            f,
                            caption=COMPLETE_TEXT
                        )
                    else:
                        bot.send_photo(
                            chat_id,
                            f,
                            caption=COMPLETE_TEXT
                        )

                return True

    return False


# =====================================
# MAIN DOWNLOAD ENGINE
# =====================================
@bot.message_handler(func=lambda message: True)
def download_media(message):
    url = message.text.strip()

    if url in ["🚀 Start Download", "📘 Help"]:
        return

    if not url.startswith("http"):
        bot.reply_to(
            message,
            "❌ Please send a valid public media link."
        )
        return

    bot.reply_to(
        message,
        "⚡ Processing your link..."
    )

    try:
        clear_downloads()

        # =====================================
        # INSTAGRAM DIRECT SUPPORT
        # =====================================
        if "instagram.com" in url:
            shortcode = None

            if "/p/" in url:
                shortcode = url.split("/p/")[1].split("/")[0]

            elif "/reel/" in url:
                shortcode = url.split("/reel/")[1].split("/")[0]

            elif "/tv/" in url:
                shortcode = url.split("/tv/")[1].split("/")[0]

            if not shortcode:
                bot.reply_to(
                    message,
                    "❌ Invalid Instagram link."
                )
                return

            post = instaloader.Post.from_shortcode(
                loader.context,
                shortcode
            )

            loader.download_post(
                post,
                target="downloads"
            )

        # =====================================
        # OTHER PLATFORMS VIA YT-DLP
        # =====================================
        else:
            ydl_opts = {
                "outtmpl": "downloads/%(title)s.%(ext)s",

                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",

                "retries": 25,
                "fragment_retries": 25,
                "extractor_retries": 15,
                "file_access_retries": 10,

                "socket_timeout": 120,
                "nocheckcertificate": True,
                "geo_bypass": True,
                "noplaylist": True,
                "quiet": True,

                "ignoreerrors": False,
                "http_chunk_size": 10485760,
                "extract_flat": False,
                "force_generic_extractor": False,
                "concurrent_fragment_downloads": 1,

                "writethumbnail": False,
                "writesubtitles": False,
                "writeautomaticsub": False,

                "prefer_insecure": False,
                "extractor_args": {
                    "youtube": {
                        "player_client": ["android", "web"]
                    }
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(
                    url,
                    download=True
                )

        # =====================================
        # SEND RESULT
        # =====================================
        if not send_downloaded_file(message.chat.id):
            bot.reply_to(
                message,
                "❌ Download failed or file not found."
            )

    except Exception as e:
        bot.reply_to(
            message,
            f"❌ Download failed\n\nReason: {str(e)}"
        )

    finally:
        clear_downloads()


# =====================================
# RUN BOT
# =====================================
print("⚡ KAMAL SYSTEM RUNNING...")
bot.infinity_polling()
