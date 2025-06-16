import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION_STRING = os.getenv("SESSION_STRING")  # Userbot session for streaming
OWNER_ID = int(os.getenv("OWNER_ID", "0"))    # Optional
