from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.exceptions import BotBlocked
bot = Bot(token='5531328946:AAGh49cMI0wtlbODR2SHq41yjLl-D7oUIy0')
back_menu = InlineKeyboardMarkup()
back_menu.add(InlineKeyboardButton('↩️', callback_data='back'))
# bot.send_photo()