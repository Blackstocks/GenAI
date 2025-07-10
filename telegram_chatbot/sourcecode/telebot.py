import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Example handler for /start command
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Hello! I'm your bot.")

# Example handler for all other messages
@dp.message()
async def echo_handler(message: Message):
    await message.answer(f"You said: {message.text}")

# Main function to run the bot
async def main():
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())