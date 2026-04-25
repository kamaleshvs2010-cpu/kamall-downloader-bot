import telebot
import instaloader
import os

TOKEN = TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
loader = instaloader.Instaloader(
    dirname_pattern="downloads",
    save_metadata=False,
    download_video_thumbnails=False,
    post_metadata_txt_pattern=""
)

WELCOME_TEXT = """
◤━━━━━━━━━━━━━━━━━━━━◥
  ⚡ KAMALL CORE ENGINE ⚡
◣━━━━━━━━━━━━━━━━━━━━◢

🚀 Premium Downloader System

━━━━━━━━━━━━━━━━━━━━━━━

📥 Instagram • YouTube • Facebook • TikTok
🎬 Reels • Posts • Shorts • Videos • HD Media

⚡ Lightning Fast Processing
🎯 Crystal Clear Output
🔥 Smart Download Engine
📦 All Platform Support

━━━━━━━━━━━━━━━━━━━━━━━

✨ Drop your link — Let the engine do the rest

👑 Powered by Kamall
📡 @KamallRoxzy
"""

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, WELCOME_TEXT)

@bot.message_handler(func=lambda message: "instagram.com" in message.text)
def download_instagram(message):
    try:
        bot.reply_to(message, "⚡ Processing your Instagram link...")

        url = message.text.strip()

        if "/p/" in url:
            shortcode = url.split("/p/")[1].split("/")[0]
        elif "/reel/" in url:
            shortcode = url.split("/reel/")[1].split("/")[0]
        else:
            bot.reply_to(message, "❌ Invalid Instagram link.")
            return

        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target="downloads")

        sent = False
        for root, dirs, files in os.walk("downloads"):
            for file in files:
                if file.endswith(".mp4") or file.endswith(".jpg"):
                    filepath = os.path.join(root, file)

                    with open(filepath, "rb") as f:
                        if file.endswith(".mp4"):
                            bot.send_video(message.chat.id, f, caption="✅ COMPLETED\n🚀 Delivered Instantly")
                        else:
                            bot.send_photo(message.chat.id, f, caption="✅ COMPLETED\n🚀 Delivered Instantly")

                    sent = True
                    break
            if sent:
                break

        if not sent:
            bot.reply_to(message, "❌ File not found.")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

print("⚡ KAMALL BOT RUNNING...")
bot.infinity_polling()
