from aiogram import *
from aiogram.dispatcher import Dispatcher
from aiogram.types import *
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData

lang_callback = CallbackData('lang', 'data')
# dep_callback = CallbackData('dep', 'type')
storage = MemoryStorage()
bot = Bot(token='5531328946:AAGh49cMI0wtlbODR2SHq41yjLl-D7oUIy0')
dp = Dispatcher(bot, storage=storage)
back_menu = InlineKeyboardMarkup()
back_menu.add(InlineKeyboardButton('↩️', callback_data='back'))
back_menu_reply = ReplyKeyboardMarkup(
    one_time_keyboard=True, resize_keyboard=True)
back_menu_reply.add(KeyboardButton('Назад'))
back_menu_en = ReplyKeyboardMarkup(
    one_time_keyboard=True, resize_keyboard=True)
back_menu_en.add(KeyboardButton('Back'))
choose_lang_start = InlineKeyboardMarkup()
choose_lang_start.add(InlineKeyboardButton('EN🇺🇸', callback_data='lang:en'),
                      InlineKeyboardButton('RU🇷🇺', callback_data='lang:ru'))
choose_lang = InlineKeyboardMarkup()
choose_lang.add(InlineKeyboardButton('EN🇺🇸', callback_data='lang:en'),
                InlineKeyboardButton('RU🇷🇺', callback_data='lang:ru'))
choose_lang.add(InlineKeyboardButton('↩️', callback_data='back'))
mainmenu = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
mainmenu.add(KeyboardButton('Купить купон🏷'))
mainmenu.add(KeyboardButton('Баланс💼'), KeyboardButton('Рефералы👤'))
mainmenu.add(KeyboardButton('Сменить язык🛠'))
mainmenu_en = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
mainmenu_en.add(KeyboardButton('Buy a coupon🏷'))
mainmenu_en.row(KeyboardButton('Balance💼'), KeyboardButton('Referrals👤'))
mainmenu_en.add(KeyboardButton('Change language🛠'))
buy_menu = InlineKeyboardMarkup()
buy_menu.add(InlineKeyboardButton('Купить', callback_data='buy'))
buy_menu.add(InlineKeyboardButton('Назад', callback_data='back'))
buy_menu_en = InlineKeyboardMarkup()
buy_menu_en.add(InlineKeyboardButton('Buy', callback_data='buy'))
buy_menu_en.add(InlineKeyboardButton('Back', callback_data='back'))
balance_menu = InlineKeyboardMarkup()
balance_menu.add(InlineKeyboardButton('Вывод', callback_data='withdraw'),
                 InlineKeyboardButton('Пополнить', callback_data='deposit'))
balance_menu.add(InlineKeyboardButton(
    'Изменить кошелёк🛠', callback_data='edit'))
balance_menu.add(InlineKeyboardButton('Назад', callback_data='back'))
balance_menu_en = InlineKeyboardMarkup()
balance_menu_en.add(InlineKeyboardButton('Withdraw', callback_data='withdraw'),
                    InlineKeyboardButton('Deposit', callback_data='deposit'))
balance_menu_en.add(InlineKeyboardButton('Edit wallet🛠', callback_data='edit'))
balance_menu_en.add(InlineKeyboardButton('Back', callback_data='back'))
edit_menu = InlineKeyboardMarkup()
edit_menu.add(InlineKeyboardButton('↩️', callback_data='back'))
dep_menu = InlineKeyboardMarkup()
# dep_menu.add(InlineKeyboardButton('USD', callback_data='dep:usd'),
#              InlineKeyboardButton('EUR', callback_data='dep:eur'))
# dep_menu.add(InlineKeyboardButton('LBL', callback_data='dep:lbl'),
#              InlineKeyboardButton('RUB', callback_data='dep:rub'))
dep_menu.add(InlineKeyboardButton('↩️', callback_data='back'))


class BuyState(StatesGroup):
    buy = State()


class WithdrawState(StatesGroup):
    withdraw = State()


class EditState(StatesGroup):
    edit = State()


class DepositState(StatesGroup):
    deposit = State()


class WalletState(StatesGroup):
    wallet = State()
