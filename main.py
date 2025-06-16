import asyncio
import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_streams import AudioPiped
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING
import yt_dlp

# Bot client
bot = Client("DJmusicplusbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
call_py = PyTgCalls(user)

# Create downloads folder
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# YT download options
ydl_opts = {
    'format': 'bestaudio',
    'quiet': True,
    'outtmpl': 'downloads/%(title)s.%(ext)s'
}

# /start
@bot.on_message(filters.command("start") & filters.private)
async def start_handler(_, message: Message):
    await message.reply("🎧 Welcome to DJmusicplusbot!\n\nUse /play in groups\nUse /ytdl or /insta in private")

# /play command (VC Audio)
@bot.on_message(filters.command("play") & filters.group)
async def play(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Please provide a YouTube link or song name.")

    query = message.text.split(None, 1)[1]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if "youtube.com" in query or "youtu.be" in query:
                info = ydl.extract_info(query, download=False)
            else:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]

            audio_url = info['url']

        await call_py.join_group_call(
            message.chat.id,
            AudioPiped(audio_url)
        )
        await message.reply(f"▶️ Now playing: {info.get('title', 'Unknown Title')}")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# /stop command
@bot.on_message(filters.command("stop") & filters.group)
async def stop(_, message: Message):
    await call_py.leave_group_call(message.chat.id)
    await message.reply("⏹️ Music stopped.")

# /ytdl - YouTube Video Downloader
@bot.on_message(filters.command("ytdl") & filters.private)
async def download_youtube(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Send a valid YouTube link.\nExample: `/ytdl https://youtu.be/xyz`")

    url = message.text.split(" ", 1)[1]
    try:
        with yt_dlp.YoutubeDL({
            'format': 'bestvideo+bestaudio',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await message.reply_video(video=filename, caption=info.get("title", "🎬"))
        os.remove(filename)
    except Exception as e:
        await message.reply(f"⚠️ Failed: {e}")

# /insta - Instagram Reel/Post Downloader
@bot.on_message(filters.command("insta") & filters.private)
async def download_instagram(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Send an Instagram post or reel link.")

    url = message.text.split(" ", 1)[1]
    
    try:
        api = f"https://savefrom.site/api/convert?url={url}"
        r = requests.get(api).json()
        video_url = r["url"]
        await message.reply_video(video_url, caption="📥 Instagram Download")
    except:
        await message.reply("⚠️ Failed to fetch video. Try another link.")

# Bot + UserBot + Call Start
async def main():
    await bot.start()
    await user.start()
    await call_py.start()
    print("✅ DJ Music Plus Bot is Running...")
    await asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    asyncio.run(main())
