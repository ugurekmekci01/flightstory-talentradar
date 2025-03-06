import telegram
import asyncio

# Function to initialize the bot with your bot token
def initialize_bot():
    bot_token = "7874755972:AAHiBDf0RYftFLfj6gbSltsJvl281O4QOgM"  # Your bot token
    chat_id = "-1002361903883"  # Your chat ID (can be a user or group chat ID)
    bot = telegram.Bot(token=bot_token)
    return bot, chat_id

# Function to send a text message asynchronously
async def send_message(message):
    bot, chat_id = initialize_bot()
    try:
        await bot.send_message(chat_id=chat_id, text=message)  # Use await here
        print(f"Message sent to {chat_id}")
    except Exception as e:
        print(f"Error sending message: {e}")

# Function to send an image asynchronously
async def send_image(image_path):
    bot, chat_id = initialize_bot()
    try:
        with open(image_path, 'rb') as image_file:
            await bot.send_photo(chat_id=chat_id, photo=image_file)  # Use await here
        print(f"Image sent to {chat_id}")
    except Exception as e:
        print(f"Error sending image: {e}")

# To run the functions asynchronously, you provide the text and image path when calling
async def run_telegram_tasks(message, image_path):
    bot, chat_id = initialize_bot()
    # Send message
    await send_message(message)
    # Send image
    await send_image(image_path)

# Function to execute the sending process
def execute_send_telegram(message, image_path):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_telegram_tasks(message, image_path))  # Pass the arguments here
