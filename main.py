import asyncio
import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_streams import AudioPiped
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING
import yt_dlp

# Bot & User Clients
bot = Client("DJMusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("DJUserBot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
call_py = PyTgCalls(user)

# Downloads folder
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# Default YTDL options
ydl_opts = {
    'format': 'bestaudio',
    'quiet': True,
    'outtmpl': 'downloads/%(title)s.%(ext)s'
}

# Start Command
@bot.on_message(filters.command("start") & filters.private)
async def start_msg(_, message: Message):
    await message.reply("🎧 Welcome to DJmusicplusbot!\n\nUse `/play` in groups\nUse `/ytdl` or `/insta` here.")

# Play Command (VC)
@bot.on_message(filters.command("play") & filters.group)
async def play_cmd(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Send a song name or YouTube link after /play")
    
    query = message.text.split(None, 1)[1]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}" if "youtu" not in query else query, download=False)
            if "entries" in info:
                info = info['entries'][0]
            audio_url = info['url']

        await call_py.join_group_call(message.chat.id, AudioPiped(audio_url))
        await message.reply(f"▶️ Now playing: {info.get('title')}")
    except Exception as e:
        await message.reply(f"⚠️ Error: {e}")

# Stop Command
@bot.on_message(filters.command("stop") & filters.group)
async def stop_cmd(_, message: Message):
    await call_py.leave_group_call(message.chat.id)
    await message.reply("⏹️ Stopped the music.")

# YouTube Downloader
@bot.on_message(filters.command("ytdl") & filters.private)
async def ytdl_cmd(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Send a YouTube link after /ytdl")
    
    url = message.text.split(None, 1)[1]
    try:
        with yt_dlp.YoutubeDL({
            'format': 'bestvideo+bestaudio',
            'outtmpl': 'downloads/%(title)s.%(ext)s'
        }) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await message.reply_video(video=filename, caption=info.get("title", "🎬 Video"))
        os.remove(filename)
    except Exception as e:
        await message.reply(f"⚠️ Download failed: {e}")

# Instagram Downloader
@bot.on_message(filters.command("insta") & filters.private)
async def insta_cmd(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Send an Instagram reel/post link after /insta")

    url = message.text.split(None, 1)[1]
    try:
        api = f"https://savefrom.site/api/convert?url={url}"
        r = requests.get(api).json()
        video_url = r["url"]
        await message.reply_video(video_url, caption="📥 Instagram Video")
    except:
        await message.reply("⚠️ Could not fetch video. Try another link.")

# Start everything
async def main():
    await bot.start()
    await user.start()
    await call_py.start()
    print("✅ DJ Music Bot is LIVE.")
    await asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    asyncio.run(main())
