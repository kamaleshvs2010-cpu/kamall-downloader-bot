import telebot
import instaloader
import yt_dlp
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

loader = instaloader.Instaloader(
    dirname_pattern="downloads",
    save_metadata=False,
    download_video_thumbnails=False,
    post_metadata_txt_pattern=""
)

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


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, WELCOME_TEXT)


@bot.message_handler(func=lambda message: True)
def download_media(message):
    url = message.text.strip()

    if not url.startswith("http"):
        bot.reply_to(message, "❌ Please send a valid social media link.")
        return

    bot.reply_to(message, "⚡ Processing your link...")

    try:
        folder = "downloads"
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Instagram direct support
        if "instagram.com" in url:
            if "/p/" in url:
                shortcode = url.split("/p/")[1].split("/")[0]
            elif "/reel/" in url:
                shortcode = url.split("/reel/")[1].split("/")[0]
            else:
                shortcode = None

            if not shortcode:
                bot.reply_to(message, "❌ Invalid Instagram link.")
                return

            post = instaloader.Post.from_shortcode(
                loader.context,
                shortcode
            )

            loader.download_post(post, target="downloads")

        # Other platforms via yt-dlp
        else:
            ydl_opts = {
                "outtmpl": "downloads/%(title)s.%(ext)s",
                "format": "best",
                "noplaylist": True,
                "quiet": True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)

        sent = False

        for root, dirs, files in os.walk("downloads"):
            for file in files:
                if file.endswith((".mp4", ".jpg", ".jpeg", ".png", ".webm", ".mkv")):
                    filepath = os.path.join(root, file)

                    with open(filepath, "rb") as f:
                        if file.endswith((".mp4", ".webm", ".mkv")):
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

                    os.remove(filepath)
                    sent = True
                    break

            if sent:
                break

        if not sent:
            bot.reply_to(message, "❌ File not found.")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


print("⚡ KAMAL SYSTEM RUNNING...")
bot.infinity_polling()
