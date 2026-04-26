import telebot
import instaloader
import re
import os
from telebot import types

# =====================================
# CONFIG
# =====================================
BOT_TOKEN = os.getenv("8210168750:AAH8NhjEoJHmI3LmxnumSi4QewW62aMTyBc")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN not found in Railway Variables")
    exit()

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# =====================================
# INSTAGRAM HIGH QUALITY LOADER
# =====================================
L = instaloader.Instaloader(
    download_pictures=True,
    download_videos=True,
    download_video_thumbnails=False,
    save_metadata=False,
    compress_json=False,
    post_metadata_txt_pattern="",
    quiet=True
)

# =====================================
# HELPER
# =====================================
def get_shortcode(url):
    match = re.search(r"/(reel|p|tv)/([^/?]+)", url)
    return match.group(2) if match else None


# =====================================
# MAIN UI TEXT
# =====================================
WELCOME_TEXT = """
╔════════════════════════════╗
║    👑 ⚡ KAMAL SYSTEM ⚡ 👑    ║
╚════════════════════════════╝

🔥 *PREMIUM INSTA DOWNLOADER*

━━━━━━━━━━━━━━━━━━━━━━

📥 High Quality Instagram Downloader

✅ Reels Download
✅ Posts Download
✅ Videos Download
✅ Carousel Download

🎯 Original HD Quality
⚡ Ultra Fast Delivery
🚀 Stable Premium Engine
💎 Smooth User Experience
🔒 Safe & Trusted Service
🌍 Fast Worldwide Access

━━━━━━━━━━━━━━━━━━━━━━

✨ Just Copy → Paste → Download

👑 Powered by Kamall System 👑
📡 @KamallRoxzy
"""

COMPLETE_TEXT = """
╔════════════════════════════╗
║      ✅ DOWNLOAD DONE      ║
╚════════════════════════════╝

⚡ Your File Is Successfully Delivered
🚀 Original Instagram Quality
💎 Premium Output Activated

━━━━━━━━━━━━━━

🔁 Send Next Instagram Link
⚡ Ready For Next Download

━━━━━━━━━━━━━━

👑 Powered by Kamall System 👑
📡 @KamallRoxzy
"""

HELP_TEXT = """
📘 *SUPPORTED INSTAGRAM LINKS*

✅ Instagram Reel
https://www.instagram.com/reel/ABC123/

✅ Instagram Post
https://www.instagram.com/p/ABC123/

✅ Instagram Video
https://www.instagram.com/tv/ABC123/

✅ Carousel Post
https://www.instagram.com/p/ABC123/

━━━━━━━━━━━━━━

⚡ Send your Instagram public link
for fast premium delivery

👑 Powered by Kamall System 👑
"""


# =====================================
# BUTTONS
# =====================================
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    btn1 = types.KeyboardButton("🚀 Start Download")
    btn2 = types.KeyboardButton("📘 Help")

    markup.add(btn1)
    markup.add(btn2)

    return markup


# =====================================
# START
# =====================================
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(
        msg.chat.id,
        WELCOME_TEXT,
        reply_markup=main_keyboard()
    )


# =====================================
# HELP BUTTON
# =====================================
@bot.message_handler(func=lambda m: m.text == "📘 Help")
def help_menu(msg):
    bot.reply_to(
        msg,
        HELP_TEXT
    )


# =====================================
# START DOWNLOAD BUTTON
# =====================================
@bot.message_handler(func=lambda m: m.text == "🚀 Start Download")
def ready(msg):
    bot.reply_to(
        msg,
        "⚡ Send your Instagram public link now."
    )


# =====================================
# MAIN DOWNLOAD ENGINE
# =====================================
@bot.message_handler(func=lambda m: True)
def handle(msg):
    if msg.text in ["🚀 Start Download", "📘 Help"]:
        return

    url = msg.text.strip()

    if "instagram.com" not in url:
        bot.reply_to(
            msg,
            "❌ Send valid Instagram Reel/Post link only."
        )
        return

    shortcode = get_shortcode(url)

    if not shortcode:
        bot.reply_to(
            msg,
            "❌ Invalid Instagram link."
        )
        return

    try:
        status = bot.send_message(
            msg.chat.id,
            """
⚡ *SYSTEM ACTIVE*

━━━━━━━━━━━━━━
⏳ Initializing Premium Engine...
"""
        )

        post = instaloader.Post.from_shortcode(
            L.context,
            shortcode
        )

        # =====================================
        # SINGLE IMAGE
        # =====================================
        if not post.is_video and post.typename != "GraphSidecar":
            bot.send_photo(
                msg.chat.id,
                post.url,
                caption=COMPLETE_TEXT
            )

        # =====================================
        # SINGLE VIDEO
        # =====================================
        elif post.is_video and post.typename != "GraphSidecar":
            bot.send_video(
                msg.chat.id,
                post.video_url,
                caption=COMPLETE_TEXT
            )

        # =====================================
        # CAROUSEL
        # =====================================
        else:
            for node in post.get_sidecar_nodes():
                if node.is_video:
                    bot.send_video(
                        msg.chat.id,
                        node.video_url
                    )
                else:
                    bot.send_photo(
                        msg.chat.id,
                        node.display_url
                    )

            bot.send_message(
                msg.chat.id,
                COMPLETE_TEXT
            )

        try:
            bot.delete_message(
                msg.chat.id,
                status.message_id
            )
        except:
            pass

    except Exception as e:
        bot.reply_to(
            msg,
            f"❌ Error:\n{str(e)}"
        )


# =====================================
# RUN BOT
# =====================================
print("⚡ KAMAL SYSTEM RUNNING...")
bot.infinity_polling()
