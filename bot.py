import telebot
import instaloader
import yt_dlp
import re
import threading
import time
import os
from queue import Queue
from telebot import types

# ========= CONFIG =========
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN not found")
    exit()

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ========= INSTAGRAM FIX =========
L = instaloader.Instaloader(
    download_pictures=False,
    download_videos=True,
    download_video_thumbnails=False,
    save_metadata=False,
    quiet=True
)

# ========= HELPERS =========
def extract_links(text):
    return re.findall(r'https?://[^\s]+', text)

def get_shortcode(url):
    m = re.search(r"/(reel|p|tv)/([^/?]+)", url)
    return m.group(2) if m else None

# ========= QUEUE =========
task_queue = Queue()

def worker():
    while True:
        msg, link = task_queue.get()
        chat_id = msg.chat.id

        try:
            # ========= STATUS UI =========
            status = bot.send_message(
                chat_id,
                """
⚡ *SYSTEM ACTIVE*

━━━━━━━━━━━━━━
⏳ Initializing engine...
"""
            )

            for step in [
                "⚡ Preparing...",
                "⚡ Fetching data...",
                "⚡ Processing...",
                "⚡ Finalizing..."
            ]:
                try:
                    bot.edit_message_text(
                        step,
                        chat_id,
                        status.message_id
                    )
                    time.sleep(0.4)
                except:
                    pass

            # ========= INSTAGRAM =========
            if "instagram.com" in link:
                shortcode = get_shortcode(link)

                if not shortcode:
                    bot.send_message(
                        chat_id,
                        "❌ Invalid Instagram link"
                    )
                    task_queue.task_done()
                    continue

                post = instaloader.Post.from_shortcode(
                    L.context,
                    shortcode
                )

                # Single image
                if not post.is_video and post.typename != "GraphSidecar":
                    bot.send_photo(
                        chat_id,
                        post.url,
                        caption="""
╔══════════════════════╗
║     ✅ COMPLETED      ║
╚══════════════════════╝

⚡ File Ready
🚀 Delivered Instantly

━━━━━━━━━━━━━━
👑 *Kamall Downloader*
📡 @KamallRoxzy
"""
                    )

                # Single video
                elif post.is_video and post.typename != "GraphSidecar":
                    bot.send_video(
                        chat_id,
                        post.video_url,
                        caption="""
╔══════════════════════╗
║     ✅ COMPLETED      ║
╚══════════════════════╝

⚡ File Ready
🚀 Delivered Instantly

━━━━━━━━━━━━━━
👑 *Kamall Downloader*
📡 @KamallRoxzy
"""
                    )

                # Carousel
                else:
                    for node in post.get_sidecar_nodes():
                        if node.is_video:
                            bot.send_video(
                                chat_id,
                                node.video_url
                            )
                        else:
                            bot.send_photo(
                                chat_id,
                                node.display_url
                            )

                    bot.send_message(
                        chat_id,
                        """
╔══════════════════════╗
║     ✅ COMPLETED      ║
╚══════════════════════╝

⚡ File Ready
🚀 Delivered Instantly

━━━━━━━━━━━━━━
👑 *Kamall Downloader*
📡 @KamallRoxzy
"""
                    )

            # ========= ALL OTHER PLATFORMS =========
            else:
                ydl_opts = {
                    "format": "bestvideo+bestaudio/best",
                    "merge_output_format": "mp4",

                    "outtmpl": "video.%(ext)s",

                    "retries": 20,
                    "fragment_retries": 20,
                    "extractor_retries": 10,
                    "file_access_retries": 5,

                    "socket_timeout": 90,
                    "nocheckcertificate": True,
                    "geo_bypass": True,
                    "noplaylist": True,
                    "quiet": True,
                    "no_warnings": True,
                    "ignoreerrors": False,

                    "http_chunk_size": 10485760,
                    "extract_flat": False,
                    "force_generic_extractor": False,
                    "concurrent_fragment_downloads": 1,

                    "extractor_args": {
                        "youtube": {
                            "player_client": ["android", "web"]
                        }
                    }
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.extract_info(link, download=True)

                # Detect actual downloaded file
                video_file = None

                for f in os.listdir():
                    if f.startswith("video."):
                        video_file = f
                        break

                if not video_file:
                    bot.send_message(
                        chat_id,
                        "❌ Download failed"
                    )
                    task_queue.task_done()
                    continue

                size = os.path.getsize(video_file)

                if size > 50 * 1024 * 1024:
                    bot.send_message(
                        chat_id,
                        "❌ File too large"
                    )
                    os.remove(video_file)
                    task_queue.task_done()
                    continue

                # Retry upload
                for i in range(3):
                    try:
                        with open(video_file, "rb") as v:
                            bot.send_video(
                                chat_id,
                                v,
                                timeout=120,
                                caption="""
╔══════════════════════╗
║     ✅ COMPLETED      ║
╚══════════════════════╝

⚡ File Ready
🚀 Delivered Instantly

━━━━━━━━━━━━━━
👑 *Kamall Downloader*
📡 @KamallRoxzy
"""
                            )
                        break

                    except:
                        if i == 2:
                            bot.send_message(
                                chat_id,
                                "❌ Upload failed"
                            )

                os.remove(video_file)

            try:
                bot.delete_message(
                    chat_id,
                    status.message_id
                )
            except:
                pass

        except Exception as e:
            bot.send_message(
                chat_id,
                f"❌ Error:\n{str(e)}"
            )

        task_queue.task_done()

# ========= START WORKERS =========
for _ in range(2):
    threading.Thread(
        target=worker,
        daemon=True
    ).start()

# ========= START BUTTON UI =========
@bot.message_handler(commands=['start'])
def start(msg):
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    btn1 = types.KeyboardButton("🚀 Start Download")
    btn2 = types.KeyboardButton("📘 Help")

    markup.add(btn1, btn2)

    text = """
╔══════════════════════╗
║   ⚡ KAMALL SYSTEM ⚡   ║
╚══════════════════════╝

🚀 *Ultimate Downloader Engine*

━━━━━━━━━━━━━━━━━━━━━━━

📥 Instagram • YouTube • Facebook • TikTok
📥 Twitter • Reddit • Vimeo

⚡ Ultra Fast Processing
🎯 Clean HD Output

━━━━━━━━━━━━━━━━━━━━━━━

✨ Just send a public link

👑 @KamallRoxzy
"""

    bot.send_message(
        msg.chat.id,
        text,
        reply_markup=markup
    )

# ========= HELP BUTTON =========
@bot.message_handler(func=lambda m: m.text == "📘 Help")
def help_menu(msg):
    bot.reply_to(
        msg,
        """
📘 Supported Platforms

✅ Instagram
✅ YouTube
✅ Facebook
✅ TikTok
✅ Twitter / X
✅ Reddit
✅ Vimeo

⚠ Public links only
❌ Private links not supported
"""
    )

# ========= START DOWNLOAD BUTTON =========
@bot.message_handler(func=lambda m: m.text == "🚀 Start Download")
def ready(msg):
    bot.reply_to(
        msg,
        "⚡ Send your public media link now."
    )

# ========= MAIN =========
@bot.message_handler(func=lambda m: True)
def handle(msg):
    if msg.text in ["🚀 Start Download", "📘 Help"]:
        return

    links = extract_links(msg.text)

    if not links:
        bot.reply_to(
            msg,
            "❌ Send valid public link"
        )
        return

    for link in links:
        task_queue.put((msg, link))

# ========= RUN =========
print("⚡ PREMIUM BOT RUNNING...")
bot.infinity_polling()
