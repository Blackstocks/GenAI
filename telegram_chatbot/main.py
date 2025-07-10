import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
import os
import sys
import openai

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
openai.api_key = os.getenv("OPEN_API_KEY")

class Reference:
    # to store previous response from the openai 
    def __init__(self) -> None:
        self.response = ""  # Changed from 'reference' to 'response'

reference = Reference()
model_name = "gpt-4o-mini"  # Changed to a valid model name

# Initializing bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

def clear_convo():
    reference.response = ""

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Hello!\nI'm your personal bot.\npowered by OpenAI")

@dp.message(Command("clear"))
async def clear_handler(message: Message):
    clear_convo()
    await message.answer("I have cleared the past conversation!!")

@dp.message(Command("help"))
async def helper_handler(message: Message):
    help_command = """
        Hi there, I'm telebot powered by OpenAI. Please follow these commands.
        /start - to start the new chat
        /clear - to clear the past conversation and context
        /help - to get this help menu
        I hope this helps. :)
    """
    await message.answer(help_command)

@dp.message()
async def openai_handler(message: Message):
    print(f">>> USER: \n\t{message.text}")
    
    # Build messages list - only include previous response if it exists
    messages = []
    if reference.response:
        messages.append({"role": "assistant", "content": reference.response})
    messages.append({"role": "user", "content": message.text})
    
    try:
        response = openai.chat.completions.create(
            model=model_name,
            messages=messages
        )
        reference.response = response.choices[0].message.content
        print(f">>> telebot: \n\t{reference.response}")
        
        # Fixed the bot.send_message call
        await bot.send_message(chat_id=message.chat.id, text=reference.response)
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        await message.answer("Sorry, I encountered an error processing your request.")

# Main function to run the bot
async def main():
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())