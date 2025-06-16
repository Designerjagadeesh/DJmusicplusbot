import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING
import yt_dlp

# Main bot client
bot = Client("DJmusicplusbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Userbot client for voice streaming
user = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# Voice call handler
call_py = PyTgCalls(user)

# YouTube download options
ydl_opts = {"format": "bestaudio", "quiet": True}

@bot.on_message(filters.command("start") & filters.private)
async def start_handler(_, message: Message):
    await message.reply("🎧 Welcome to DJmusicplusbot!\nUse /play <YouTube link> in a group to start music.")

@bot.on_message(filters.command("play") & filters.group)
async def play(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Please provide a YouTube link.")
    
    url = message.command[1]
    chat_id = message.chat.id

    # Get YouTube audio URL
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']
    
    # Stream audio in group
    await call_py.join_group_call(chat_id, AudioPiped(audio_url))
    await message.reply(f"▶️ Now Playing:\n{info.get('title', 'Unknown Title')}")

@bot.on_message(filters.command("stop") & filters.group)
async def stop(_, message: Message):
    await call_py.leave_group_call(message.chat.id)
    await message.reply("⏹️ Music stopped.")

# Run the bot and userbot
async def main():
    await bot.start()
    await user.start()
    await call_py.start()
    print("✅ DJ Music Plus Bot is running...")
    await asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    asyncio.run(main())
