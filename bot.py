import telebot
import instaloader
import yt_dlp
import os

# =========================
# BOT TOKEN (Railway Variable)
# =========================
TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

# =========================
# INSTAGRAM LOADER
# =========================
loader = instaloader.Instaloader(
    dirname_pattern="downloads",
    save_metadata=False,
    download_video_thumbnails=False,
    post_metadata_txt_pattern=""
)

# =========================
# START UI
# =========================
WELCOME_TEXT = """
◤━━━━━━━━━━━━━━━━━━━━◥
  ⚡ KAMAL SYSTEM ⚡
◣━━━━━━━━━━━━━━━━━━━━◢

🚀 Premium Downloader System

━━━━━━━━━━━━━━━━━━━━

📥 Instagram • YouTube • Facebook • TikTok
🎬 Reels • Posts • Shorts • Videos • HD Media

⚡ Lightning Fast Processing
🎯 Crystal Clear Output
🔥 Smart Download Engine
📦 All Platform Support

━━━━━━━━━━━━━━━━━━━━

✨ Drop your link — Let the engine do the rest

👑 Powered by Kamall System 👑
📡 @KamallRoxzy
"""

# =========================
# COMPLETE UI
# =========================
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

# =========================
# /START COMMAND
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, WELCOME_TEXT)

# =========================
# MAIN DOWNLOAD ENGINE
# =========================
@bot.message_handler(func=lambda message: True)
def download_media(message):
    url = message.text.strip()

    if not url.startswith("http"):
        bot.reply_to(
            message,
            "❌ Please send a valid social media link."
        )
        return

    bot.reply_to(
        message,
        "⚡ Processing your link..."
    )

    try:
        # Create folder if not exists
        if not os.path.exists("downloads"):
            os.makedirs("downloads")

        # =========================
        # INSTAGRAM DIRECT SUPPORT
        # =========================
        if "instagram.com" in url:
            if "/p/" in url:
                shortcode = url.split("/p/")[1].split("/")[0]

            elif "/reel/" in url:
                shortcode = url.split("/reel/")[1].split("/")[0]

            elif "/tv/" in url:
                shortcode = url.split("/tv/")[1].split("/")[0]

            else:
                shortcode = None

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

        # =========================
        # ALL OTHER PLATFORMS
        # =========================
        else:
            ydl_opts = {
                "outtmpl": "downloads/%(title)s.%(ext)s",
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
                "noplaylist": True,
                "quiet": True,
                "nocheckcertificate": True,
                "ignoreerrors": False,
                "geo_bypass": True,
                "retries": 10,
                "fragment_retries": 10,
                "socket_timeout": 30
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(
                    url,
                    download=True
                )

        # =========================
        # SEND FILE TO USER
        # =========================
        sent = False

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
                    filepath = os.path.join(
                        root,
                        file
                    )

                    with open(filepath, "rb") as f:
                        if file.endswith((
                            ".mp4",
                            ".webm",
                            ".mkv"
                        )):
                            bot.send_video(
                                message.chat.id,
                                f,
                                caption=COMPLETE_TEXT
                            )
                        else:
                            bot.send_photo(
                                message.chat.id,
                                f,
                                caption=COMPLETE_TEXT
                            )

                    # delete after sending
                    os.remove(filepath)

                    sent = True
                    break

            if sent:
                break

        if not sent:
            bot.reply_to(
                message,
                "❌ File not found."
            )

    except Exception as e:
        bot.reply_to(
            message,
            f"❌ Error: {str(e)}"
        )

# =========================
# RUN BOT
# =========================
print("⚡ KAMAL SYSTEM RUNNING...")
bot.infinity_polling()
