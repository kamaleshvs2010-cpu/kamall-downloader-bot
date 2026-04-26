import telebot
import instaloader
import yt_dlp
import re
import threading
import time
import os
from queue import Queue

# ========= CONFIG =======
BOT_TOKEN = os.getenv("8210168750:AAH8NhjEoJHmI3LmxnumSi4QewW62aMTyBc")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# INSTAGRAM FIX
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
            # 🔥 UI SAME
            status = bot.send_message(chat_id,
"""
⚡ *SYSTEM ACTIVE*

━━━━━━━━━━━━━━
⏳ Initializing engine...
""")

            for f in [
                "⚡ Preparing...",
                "⚡ Fetching data...",
                "⚡ Processing...",
                "⚡ Finalizing..."
            ]:
                try:
                    bot.edit_message_text(f, chat_id, status.message_id)
                    time.sleep(0.3)
                except:
                    pass

            # ========= INSTAGRAM =========
            if "instagram.com" in link:
                shortcode = get_shortcode(link)

                if not shortcode:
                    bot.send_message(chat_id, "❌ Invalid Instagram link")
                    task_queue.task_done()
                    continue

                post = instaloader.Post.from_shortcode(L.context, shortcode)

                # IMAGE
                if not post.is_video and post.typename != "GraphSidecar":
                    bot.send_photo(chat_id, post.url, caption="""
╔══════════════════════╗
║     ✅ COMPLETED      ║
╚══════════════════════╝

⚡ File Ready  
🚀 Delivered Instantly  

━━━━━━━━━━━━━━
👑 *Kamall Downloader*
📡 @KamallRoxzy
""")

                # VIDEO
                elif post.is_video and post.typename != "GraphSidecar":
                    bot.send_video(chat_id, post.video_url, caption="""
╔══════════════════════╗
║     ✅ COMPLETED      ║
╚══════════════════════╝

⚡ File Ready  
🚀 Delivered Instantly  

━━━━━━━━━━━━━━
👑 *Kamall Downloader*
📡 @KamallRoxzy
""")

                # CAROUSEL
                else:
                    for node in post.get_sidecar_nodes():
                        if node.is_video:
                            bot.send_video(chat_id, node.video_url)
                        else:
                            bot.send_photo(chat_id, node.display_url)

                    bot.send_message(chat_id, """
╔══════════════════════╗
║     ✅ COMPLETED      ║
╚══════════════════════╝

⚡ File Ready  
🚀 Delivered Instantly  

━━━━━━━━━━━━━━
👑 *Kamall Downloader*
📡 @KamallRoxzy
""")

            # ========= ALL OTHER PLATFORMS =========
            else:
                ydl_opts = {
                    'format': 'best[ext=mp4]',
                    'outtmpl': 'video.mp4',
                    'quiet': True,
                    'retries': 5,
                    'fragment_retries': 5,
                    'socket_timeout': 30,
                    'nocheckcertificate': True,
                    'ignoreerrors': True,
                    'no_warnings': True
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([link])

                if not os.path.exists("video.mp4"):
                    bot.send_message(chat_id, "❌ Download failed")
                    task_queue.task_done()
                    continue

                size = os.path.getsize("video.mp4")

                if size > 50 * 1024 * 1024:
                    bot.send_message(chat_id, "❌ File too large")
                    os.remove("video.mp4")
                    task_queue.task_done()
                    continue

                # RETRY UPLOAD
                for i in range(3):
                    try:
                        with open("video.mp4", "rb") as v:
                            bot.send_video(chat_id, v, timeout=120, caption="""
╔══════════════════════╗
║     ✅ COMPLETED      ║
╚══════════════════════╝

⚡ File Ready  
🚀 Delivered Instantly  

━━━━━━━━━━━━━━
👑 *Kamall Downloader*
📡 @KamallRoxzy
""")
                        break
                    except:
                        if i == 2:
                            bot.send_message(chat_id, "❌ Upload failed")

                os.remove("video.mp4")

            bot.delete_message(chat_id, status.message_id)

        except Exception as e:
            bot.send_message(chat_id, f"❌ Error:\n{e}")

        task_queue.task_done()

# START WORKERS
for _ in range(2):
    threading.Thread(target=worker, daemon=True).start()

# ========= START =========
@bot.message_handler(commands=['start'])
def start(msg):
    text = """
╔══════════════════════╗
║   ⚡ KAMALL SYSTEM ⚡   ║
╚══════════════════════╝

🚀 *Ultimate Downloader Engine*

━━━━━━━━━━━━━━━━━━━━━━━

📥 Instagram • YouTube • Facebook • TikTok • Twitter • Reddit • Vimeo  
⚡ Ultra Fast Processing  
🎯 Clean HD Output  

━━━━━━━━━━━━━━━━━━━━━━━

✨ _Just send a link and watch the magic_

👑 @KamallRoxzy
"""
    bot.send_message(msg.chat.id, text)

# ========= MAIN =========
@bot.message_handler(func=lambda m: True)
def handle(msg):
    links = extract_links(msg.text)

    if not links:
        bot.reply_to(msg, "❌ Send valid link")
        return

    for link in links:
        task_queue.put((msg, link))

# ========= RUN =========
print("⚡ PREMIUM BOT RUNNING...")
bot.infinity_polling()
