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
✅ Many yt-dlp Supported Platforms

━━━━━━━━━━━━━━━━━━━━

⚡ Strong Support
⚠ Weak Links Often Work
❌ Private Content Not Supported

━━━━━━━━━━━━━━━━━━━━

📥 Public Links Only
🎯 HD Output
🔥 Smart Download Engine

━━━━━━━━━━━━━━━━━━━━

✨ Send ONE link only per message

⚠ Private accounts not supported
⚠ Login required content not supported
⚠ Some Facebook share links may fail

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

HELP_TEXT = """
📘 HOW TO USE

1. Send Supported Links⚡[ Acc To Guidelines ]

2. Strong Support:
✅ Instagram Reel / Post
✅ YouTube Video / Shorts
✅ Facebook Public Video
✅ TikTok Public Video

3. Weak But Often Works:
⚠ Facebook Share Links
⚠ fb.watch Links
⚠ Twitter/X Shared Media
⚠ Reddit Shared Videos

4. Not Supported:
❌ Private accounts
❌ Login required content
❌ Protected videos
❌ Expired links

⚠ Best Result:
Use direct public video links only
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
    bot.reply_to(message, HELP_TEXT)


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
# CLEAN DOWNLOAD FOLDER
# =====================================
def clear_downloads():
    if os.path.exists("downloads"):
        try:
            shutil.rmtree("downloads")
        except:
            pass
    os.makedirs("downloads", exist_ok=True)


# =====================================
# SEND FILE TO USER
# =====================================
def send_downloaded_file(chat_id):
    for root, dirs, files in os.walk("downloads"):
        for file in files:
            if file.endswith((
                ".mp4", ".jpg", ".jpeg",
                ".png", ".webm", ".mkv"
            )):
                filepath = os.path.join(root, file)

                with open(filepath, "rb") as f:
                    if file.endswith((
                        ".mp4", ".webm", ".mkv"
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
            "❌ Please send one valid public social media link."
        )
        return

    if " " in url:
        bot.reply_to(
            message,
            "❌ Send only ONE link per message."
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

                "retries": 20,
                "fragment_retries": 20,
                "extractor_retries": 10,
                "file_access_retries": 5,

                "socket_timeout": 90,
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
                "writeautomaticsub": False
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
        if "facebook.com" in url:
            bot.reply_to(
                message,
                """
❌ Facebook link failed

⚠ Facebook share links may work or fail

Supported Best:
✅ facebook.com/username/videos/123456789/

Weak But Often Works:
⚠ facebook.com/share/xxxxx/
⚠ fb.watch/xxxxx/

Not Supported:
❌ Private videos
❌ Login required content

⚡ Please send direct public video link
"""
            )

        elif "youtube.com" in url or "youtu.be" in url:
            bot.reply_to(
                message,
                """
❌ YouTube link failed

Possible reasons:
• Private video
• Age restriction
• Login required
• Region lock

Best Format:
✅ youtube.com/shorts/VIDEO_ID
✅ youtu.be/VIDEO_ID
"""
            )

        elif "instagram.com" in url:
            bot.reply_to(
                message,
                """
❌ Instagram link failed

Supported:
✅ Public Reels
✅ Public Posts

Not Supported:
❌ Private accounts
❌ Restricted content
"""
            )

        elif "tiktok.com" in url:
            bot.reply_to(
                message,
                """
❌ TikTok link failed

Possible reasons:
• Private video
• Region restriction
• Protected content

Best Format:
✅ tiktok.com/@user/video/123456789
"""
            )

        else:
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
