import telegram
import asyncio

# Function to initialize the bot
def initialize_bot():
    bot_token = "7491505014:AAHAq0TLsL7rCgJVUZeJbXiX9hxqEpB-YIw"  # Your bot token
    chat_id = "-1002288312500"  # Your chat ID (can be a user or group chat ID)
    bot = telegram.Bot(token=bot_token)
    return bot, chat_id

# Function to send a text message asynchronously
async def send_message(message):
    bot, chat_id = initialize_bot()
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        print(f"Message sent to {chat_id}")
    except Exception as e:
        print(f"Error sending message: {e}")

# Function to send an image asynchronously
async def send_image(image_path):
    bot, chat_id = initialize_bot()
    try:
        with open(image_path, 'rb') as image_file:
            await bot.send_photo(chat_id=chat_id, photo=image_file)
        print(f"Image sent to {chat_id}")
    except Exception as e:
        print(f"Error sending image: {e}")

# Function to run both tasks
async def run_telegram_tasks(message, image_path):
    await send_message(message)
    await send_image(image_path)

# ✅ Fix: Use `asyncio.run()` instead of `get_event_loop()`
def send_to_telegram(message, image_path):
    asyncio.run(run_telegram_tasks(message, image_path))
