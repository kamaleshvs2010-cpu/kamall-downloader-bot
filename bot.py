import telebot
import instaloader
import re
import os
import time
import shutil

# =====================================
# CONFIG FOR RAILWAY
# =====================================

# Railway → Variables
# KEY   = BOT_TOKEN
# VALUE = your real Telegram bot token

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN not found")
    exit()

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# =====================================
# INSTAGRAM LOADER
# =====================================

L = instaloader.Instaloader(
    save_metadata=False,
    download_comments=False,
    post_metadata_txt_pattern="",
    download_video_thumbnails=False,
    quiet=True
)

# =====================================
# DOWNLOAD FUNCTION
# =====================================

def download_reel(url):
    try:
        match = re.search(r"/reel/([^/]+)/", url)

        if not match:
            return None

        shortcode = match.group(1)

        post = instaloader.Post.from_shortcode(
            L.context,
            shortcode
        )

        L.download_post(post, target=shortcode)

        if os.path.exists(shortcode):
            for file in os.listdir(shortcode):
                if file.endswith(".mp4"):
                    return os.path.join(shortcode, file)

        return None

    except Exception as e:
        print(f"Download Error: {e}")
        return None


# =====================================
# START / HELP
# =====================================

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    welcome_text = """
╔══════════════════════════════════════╗
║   👑⚡ KAMALL INSTA DOWNLOADER ⚡👑   ║
╠══════════════════════════════════════╣
║  📥 Send Any Instagram Reel URL      ║
║  🚀 Instant High Quality Download    ║
║  🎬 HD Reel Video Fast Delivery      ║
║  🔥 Premium • Safe • Trusted         ║
║  💎 Smooth & Powerful Experience     ║
╠══════════════════════════════════════╣
║  📌 Example:                         ║
║  https://www.instagram.com/reel/xxx  ║
╠══════════════════════════════════════╣
║      👑 Powered by Kamall 👑         ║
║        📡 @KamallRoxzy               ║
╚══════════════════════════════════════╝
"""

    bot.reply_to(message, welcome_text)


# =====================================
# MAIN HANDLER
# =====================================

@bot.message_handler(func=lambda msg: True)
def handle_message(msg):
    url = msg.text.strip()

    if "instagram.com" not in url:
        bot.reply_to(
            msg,
            "❌ Please send a valid Instagram Reel link."
        )
        return

    processing_msg = bot.reply_to(
        msg,
        "⏳ Processing your reel...\nPlease wait..."
    )

    file_path = download_reel(url)

    if file_path:
        try:
            with open(file_path, "rb") as video:
                bot.send_video(
                    msg.chat.id,
                    video,
                    caption="""
✅ Download Complete!

📹 Reel downloaded successfully
💫 Enjoy your video!

👑 Powered by Kamall
📡 @KamallRoxzy
"""
                )

            try:
                bot.delete_message(
                    msg.chat.id,
                    processing_msg.message_id
                )
            except:
                pass

        except Exception as e:
            print(f"Upload Error: {e}")
            bot.reply_to(
                msg,
                "❌ Upload failed. Try again."
            )

        # Cleanup
        try:
            os.remove(file_path)

            match = re.search(r"/reel/([^/]+)/", url)
            if match:
                shortcode = match.group(1)

                if os.path.exists(shortcode):
                    shutil.rmtree(shortcode)

        except:
            pass

    else:
        bot.reply_to(
            msg,
            """
❌ Download Failed

Possible reasons:
• Private account
• Invalid reel link
• Instagram blocked request
• Temporary issue

Try again later.
"""
        )


# =====================================
# START BOT
# =====================================

print("⚡ KAMALL INSTA DOWNLOADER RUNNING...")

while True:
    try:
        bot.infinity_polling(
            timeout=60,
            long_polling_timeout=30
        )
    except Exception as e:
        print(f"Restarting bot due to error: {e}")
        time.sleep(5)
