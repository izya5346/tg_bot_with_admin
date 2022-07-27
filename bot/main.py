import os
from decimal import Decimal
from config import *
import models
from utils import *
import logging
logging.basicConfig(level=logging.DEBUG)
# filename='bot.log', filemode='w',


@dp.message_handler(commands=['set_group'])
async def process_group(message: types.Message):
    if message.chat.type == 'group':
        group = await models.Setting.get(label='Группа')
        group.value.update({'group_id': str(message.chat.id)})
        await group.save()
        await bot.send_message(message.chat.id, "Группа успешно сконфигурирована")


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    try:
        user, created = await models.User.get_or_create(chat_id=message.from_user.id, username=message.from_user.username)
    except:
        user = await models.User.get(chat_id=message.from_user.id)
        user.username = message.from_user.username
        await user.save()
        created = False
    msg = models.Message(text=message.text, user=user)
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    await msg.save()
    try:
        refered = message.text.split()
        data = refered[1]
        if created:
            await user.add_to_refs(data)
    except Exception as e:
        pass
    if created:
        await user.generate_refcode()
        if getmsg['/start Сменить язык🛠']['image']:
            await bot.send_photo(message.from_user.id, getmsg['/start Сменить язык🛠']['image'], getmsg['/start Сменить язык🛠']['en'], reply_markup=choose_lang_start)
        else:
            await bot.send_message(message.from_user.id, getmsg['/start Сменить язык🛠']['en'], reply_markup=choose_lang_start)
    else:
        if getmsg['/start']['image']:
            match user.lang:
                case 'ru':
                    await bot.send_photo(message.from_user.id, getmsg['/start']['image'], getmsg['/start']['ru'], reply_markup=mainmenu)
                case 'en':
                    await bot.send_photo(message.from_user.id, getmsg['/start']['image'], getmsg['/start']['en'], reply_markup=mainmenu_en)
        else:
            match user.lang:
                case 'ru':
                    await bot.send_message(message.from_user.id, getmsg['/start']['ru'], reply_markup=mainmenu)
                case 'en':
                    await bot.send_message(message.from_user.id, getmsg['/start']['en'], reply_markup=mainmenu_en)


@dp.callback_query_handler(lang_callback.filter())
async def lang_settings(call: CallbackQuery, callback_data: dict):
    user = await models.User.get(chat_id=call.from_user.id)
    msg = models.Message(text=call.data, user=user)
    await msg.save()
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    match callback_data['data']:
        case 'en':
            await bot.send_message(call.from_user.id, getmsg['Готово']['en'], reply_markup=mainmenu_en)
            user.lang = 'en'
            await user.save()
        case 'ru':
            await bot.send_message(call.from_user.id, getmsg['Готово']['ru'], reply_markup=mainmenu)
            user.lang = 'ru'
            await user.save()


@dp.message_handler()
async def echo_message(message: types.Message):
    user = await models.User.get(chat_id=message.from_user.id)
    msg = models.Message(text=message.text, user=user)
    amount = await models.Setting.get(label='Стоимость').values()
    await msg.save()
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    match user.lang:
        case 'ru':
            match message.text:
                case 'Купить купон🏷':
                    if getmsg['Купить купон🏷']['image']:
                        await bot.send_photo(message.from_user.id, getmsg['Купить купон🏷']['image'], getmsg['Купить купон🏷']['ru'].format(amount['value']['coupon']), reply_markup=buy_menu, parse_mode='Markdown')
                    else:
                        await bot.send_message(message.from_user.id, getmsg['Купить купон🏷']['ru'].format(amount['value']['coupon']), reply_markup=buy_menu, parse_mode='Markdown')
                case 'Баланс💼':
                    coups = await models.Coupon.filter(user=user)
                    if coups:
                        coups = [' '.join(i.arr['coupon'])
                                 for i in coups]
                        if getmsg['Баланс💼']['image']:
                            await bot.send_photo(message.from_user.id, getmsg['Баланс💼']['image'], getmsg['Баланс💼']['ru'].format(user.balance, '\n'.join(coups)), reply_markup=balance_menu, parse_mode='Markdown')
                        else:
                            await bot.send_message(message.from_user.id, getmsg['Баланс💼']['ru'].format(user.balance, '\n'.join(coups)), reply_markup=balance_menu, parse_mode='Markdown')
                    else:
                        if getmsg['Баланс💼(кратко)']['image']:
                            await bot.send_photo(message.from_user.id, getmsg['Баланс💼(кратко)']['image'], getmsg['Баланс💼(кратко)']['ru'].format(user.balance), reply_markup=balance_menu)
                        else:
                            await bot.send_message(message.from_user.id, getmsg['Баланс💼(кратко)']['ru'].format(user.balance), reply_markup=balance_menu)
                case 'Рефералы👤':
                    if getmsg['Рефералы👤']['image']:
                        await bot.send_photo(message.from_user.id, getmsg['Рефералы👤']['image'], getmsg['Рефералы👤']['ru'].format(user.count_refs, user.count_refs_2nd, user.refcode), reply_markup=back_menu)
                    else:
                        await bot.send_message(message.from_user.id, getmsg['Рефералы👤']['ru'].format(user.count_refs, user.count_refs_2nd, user.refcode), reply_markup=back_menu)
                case 'Сменить язык🛠':
                    if getmsg['Сменить язык🛠']['image']:
                        await bot.send_photo(message.from_user.id, getmsg['Сменить язык🛠']['image'], getmsg['Сменить язык🛠']['ru'], reply_markup=choose_lang)
                    else:
                        await bot.send_message(message.from_user.id, getmsg['Сменить язык🛠']['ru'], reply_markup=choose_lang)
                case 'Назад':
                    if getmsg['Главное меню']['image']:
                        await bot.send_photo(message.from_user.id, getmsg['Главное меню']['image'], getmsg['Главное меню']['ru'], reply_markup=mainmenu)
                    else:
                        await bot.send_message(message.from_user.id, getmsg['Главное меню']['ru'], reply_markup=mainmenu)
                case _:
                    await bot.send_message(message.from_user.id, 'Я тебя не понимаю', reply_markup=mainmenu)
        case 'en':
            match message.text:
                case 'Buy a coupon🏷':
                    if getmsg['Купить купон🏷']['image']:
                        await bot.send_message(message.from_user.id, getmsg['Купить купон🏷']['image'], getmsg['Купить купон🏷']['en'].format(amount['value']['coupon']), reply_markup=buy_menu_en, parse_mode='Markdown')
                    else:
                        await bot.send_message(message.from_user.id, getmsg['Купить купон🏷']['en'].format(amount['value']['coupon']), reply_markup=buy_menu_en, parse_mode='Markdown')
                case 'Balance💼':
                    coups = await models.Coupon.filter(user=user)
                    if coups:
                        coups = [' '.join(i.arr['coupon'])
                                 for i in coups]
                        if getmsg['Баланс💼']['image']:
                            await bot.send_photo(message.from_user.id, getmsg['Баланс💼']['image'], getmsg['Баланс💼']['en'].format(user.balance, '\n'.join(coups)), reply_markup=balance_menu_en, parse_mode='Markdown')
                        else:
                            await bot.send_message(message.from_user.id, getmsg['Баланс💼']['en'].format(user.balance, '\n'.join(coups)), reply_markup=balance_menu_en, parse_mode='Markdown')
                    else:
                        if getmsg['Баланс💼(кратко)']['image']:
                            await bot.send_photo(message.from_user.id, getmsg['Баланс💼(кратко)']['image'], getmsg['Баланс💼(кратко)']['en'].format(user.balance), reply_markup=balance_menu_en)
                        else:
                            await bot.send_message(message.from_user.id, getmsg['Баланс💼(кратко)']['en'].format(user.balance), reply_markup=balance_menu_en)
                case 'Referrals👤':
                    if getmsg['Рефералы👤']['image']:
                        await bot.send_photo(message.from_user.id, getmsg['Рефералы👤']['image'], getmsg['Рефералы👤']['en'].format(user.count_refs, user.count_refs_2nd, user.refcode), reply_markup=back_menu_en)
                    else:
                        await bot.send_message(message.from_user.id, getmsg['Рефералы👤']['en'].format(user.count_refs, user.count_refs_2nd, user.refcode), reply_markup=back_menu_en)
                case 'Change language🛠':
                    if getmsg['Сменить язык🛠']['image']:
                        await bot.send_photo(message.from_user.id, getmsg['Сменить язык🛠']['image'], getmsg['Сменить язык🛠']['en'], reply_markup=choose_lang)
                    else:
                        await bot.send_message(message.from_user.id, getmsg['Сменить язык🛠']['en'], reply_markup=choose_lang)
                case 'Back':
                    if getmsg['Главное меню']['image']:
                        await bot.send_photo(message.from_user.id, getmsg['Главное меню']['image'], getmsg['Главное меню']['en'], reply_markup=mainmenu_en)
                    else:
                        await bot.send_message(message.from_user.id, getmsg['Главное меню']['en'], reply_markup=mainmenu_en)
                case _:
                    await bot.send_message(message.from_user.id, "I don't understand you", reply_markup=mainmenu_en)


@dp.callback_query_handler(text='back')
async def inline_back(call: CallbackQuery):
    user = await models.User.get(chat_id=call.from_user.id)
    msg = models.Message(text=call.data, user=user)
    await msg.save()
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    # await models.Message(text=, user=user).create()
    if getmsg['Главное меню']['image']:
        match user.lang:
            case 'ru':
                await bot.send_photo(call.from_user.id, getmsg['Главное меню']['image'], getmsg['Главное меню']['ru'], reply_markup=mainmenu)
            case 'en':
                await bot.send_photo(call.from_user.id, getmsg['Главное меню']['image'], getmsg['Главное меню']['en'], reply_markup=mainmenu_en)
    else:
        match user.lang:
            case 'ru':
                await bot.send_message(call.from_user.id, getmsg['Главное меню']['ru'], reply_markup=mainmenu)
            case 'en':
                await bot.send_message(call.from_user.id, getmsg['Главное меню']['en'], reply_markup=mainmenu_en)


@dp.callback_query_handler(text='buy')
async def buy(call: CallbackQuery):
    user = await models.User.get(chat_id=call.from_user.id)
    msg = models.Message(text=call.data, user=user)
    await msg.save()
    amount = await models.Setting.get(label='Стоимость').values()
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    if user.balance - Decimal(amount['value']['coupon']) >= 0:
        await BuyState.buy.set()
        match user.lang:
            case 'ru':
                await bot.send_message(call.from_user.id, getmsg['Купить']['ru'], reply_markup=back_menu, parse_mode='Markdown')
            case 'en':
                await bot.send_message(call.from_user.id, getmsg['Купить']['en'], reply_markup=back_menu_en, parse_mode='Markdown')
    else:
        match user.lang:
            case 'ru':
                await bot.send_message(call.from_user.id, getmsg['Недостаточно средств']['ru'].format(user.balance), reply_markup=mainmenu)
            case 'en':
                await bot.send_message(call.from_user.id, getmsg['Недостаточно средств']['en'].format(user.balance), reply_markup=mainmenu_en)


@dp.message_handler(state=BuyState.buy)
async def check_and_buy(message: types.Message, state: FSMContext):
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    amount = await models.Setting.get(label='Стоимость').values()
    user = await models.User.get(chat_id=message.from_user.id)
    msg = models.Message(text=message.text, user=user)
    await msg.save()
    checked, coup = check_coupon(message.text)
    if checked:
        coupon = models.Coupon()
        hs = models.History(type='buy', amount=Decimal(
            amount['value']['coupon']), user=user)
        await hs.save()
        coupon.arr.update({'coupon': coup})
        coupon.user = user
        await coupon.pay_to_refs()
        await coupon.save()
        user.balance -= Decimal(amount['value']['coupon'])
        await user.save()
        await state.finish()
        match user.lang:
            case 'ru':
                await bot.send_message(message.from_user.id, getmsg['Купон приобретён']['ru'].format(' '.join(coup)), reply_markup=mainmenu, parse_mode='Markdown')
            case 'en':
                await bot.send_message(message.from_user.id, getmsg['Купон приобретён']['en'].format(' '.join(coup)), reply_markup=mainmenu_en, parse_mode='Markdown')
    else:
        match user.lang:
            case 'ru':
                await bot.send_message(message.from_user.id, getmsg['Неверный купон']['ru'], reply_markup=back_menu, parse_mode='Markdown')
            case 'en':
                await bot.send_message(message.from_user.id, getmsg['Неверный купон']['en'], reply_markup=back_menu, parse_mode='Markdown')


@dp.callback_query_handler(state=BuyState.buy, text='back')
async def back_from_buy(call: types.CallbackQuery, state: FSMContext):
    user = await models.User.get(chat_id=call.from_user.id)
    msg = models.Message(text=call.data, user=user)
    await msg.save()
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    msg = models.Message(text=call.data, user=user)
    await msg.save()
    await state.finish()
    # await models.Message(text=, user=user).create()
    if getmsg['Главное меню']['image']:
        match user.lang:
            case 'ru':
                await bot.send_photo(call.from_user.id, getmsg['Главное меню']['image'], getmsg['Главное меню']['ru'], reply_markup=mainmenu)
            case 'en':
                await bot.send_photo(call.from_user.id, getmsg['Главное меню']['image'], getmsg['Главное меню']['en'], reply_markup=mainmenu_en)
    else:
        match user.lang:
            case 'ru':
                await bot.send_message(call.from_user.id, getmsg['Главное меню']['ru'], reply_markup=mainmenu)
            case 'en':
                await bot.send_message(call.from_user.id, getmsg['Главное меню']['en'], reply_markup=mainmenu_en)


@dp.callback_query_handler(text='withdraw')
async def withdraw(call: CallbackQuery):
    user = await models.User.get(chat_id=call.from_user.id)
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    msg = models.Message(text=call.data, user=user)
    await msg.save()
    if user.wallet:
        if user.balance > 0:
            await WithdrawState.withdraw.set()
            match user.lang:
                case 'ru':
                    await bot.send_message(call.from_user.id, getmsg['Сумму для вывода']['ru'].format(user.balance), reply_markup=back_menu)
                case 'en':
                    await bot.send_message(call.from_user.id, getmsg['Сумму для вывода']['en'].format(user.balance), reply_markup=back_menu)
    else:
        await WalletState.wallet.set()
        match user.lang:
            case 'ru':
                await bot.send_message(call.from_user.id, getmsg['Введите кошелёк']['ru'], reply_markup=back_menu)
            case 'en':
                await bot.send_message(call.from_user.id, getmsg['Введите кошелёк']['en'], reply_markup=back_menu)


@dp.message_handler(state=WithdrawState.withdraw)
async def check_and_withdraw(message: types.Message, state: FSMContext):
    group = await models.Setting.get(label='Группа').values()
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    user = await models.User.get(chat_id=message.from_user.id)
    msg = models.Message(text=message.text, user=user)
    await msg.save()
    if user.balance - Decimal(message.text) >= 0:
        user.balance -= Decimal(message.text)
        hs = models.History(
            type='out', amount=Decimal(message.text), user=user)
        await hs.save()
        await user.save()
        await state.finish()
        match user.lang:
            case 'ru':
                await bot.send_message(message.from_user.id, getmsg['Вывод успешен']['ru'], reply_markup=mainmenu)
            case 'en':
                await bot.send_message(message.from_user.id, getmsg['Вывод успешен']['en'], reply_markup=mainmenu_en)
        await bot.send_message(group['value']['group_id'], 'Запрос на вывод:\nНик: @{}\nСумма: {}\nКошелёк получателя: {}\n'.format(user.username, str(Decimal(message.text)), user.wallet))
    else:
        match user.lang:
            case 'ru':
                await bot.send_message(message.from_user.id, getmsg['Недостаточно средств']['ru'].format(user.balance), reply_markup=mainmenu)
            case 'en':
                await bot.send_message(message.from_user.id, getmsg['Недостаточно средств']['en'].format(user.balance), reply_markup=mainmenu_en)


@dp.callback_query_handler(state=WithdrawState.withdraw, text='back')
async def back_from_with(call: types.CallbackQuery, state: FSMContext):
    user = await models.User.get(chat_id=call.from_user.id)
    msg = models.Message(text=call.data, user=user)
    await msg.save()
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    msg = models.Message(text=call.data, user=user)
    await msg.save()
    await state.finish()
    if getmsg['Главное меню']['image']:
        match user.lang:
            case 'ru':
                await bot.send_photo(call.from_user.id, getmsg['Главное меню']['image'], getmsg['Главное меню']['ru'], reply_markup=mainmenu)
            case 'en':
                await bot.send_photo(call.from_user.id, getmsg['Главное меню']['image'], getmsg['Главное меню']['en'], reply_markup=mainmenu_en)
    else:
        match user.lang:
            case 'ru':
                await bot.send_message(call.from_user.id, getmsg['Главное меню']['ru'], reply_markup=mainmenu)
            case 'en':
                await bot.send_message(call.from_user.id, getmsg['Главное меню']['en'], reply_markup=mainmenu_en)


@dp.message_handler(state=WalletState.wallet)
async def add_wallet(message: types.Message, state: FSMContext):
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    user = await models.User.get(chat_id=message.from_user.id)
    msg = models.Message(text=message.text, user=user)
    await msg.save()
    user.wallet = message.text.lower()
    await user.save()
    await state.finish()
    match user.lang:
        case 'ru':
            await bot.send_message(message.from_user.id, getmsg['Кошелёк добавлен']['ru'], reply_markup=balance_menu)
        case 'en':
            await bot.send_message(message.from_user.id, getmsg['Кошелёк добавлен']['en'], reply_markup=balance_menu_en)


@dp.callback_query_handler(state=WalletState.wallet, text='back')
async def back_from_wall(call: types.CallbackQuery, state: FSMContext):
    user = await models.User.get(chat_id=call.from_user.id)
    msg = models.Message(text=call.data, user=user)
    await msg.save()
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    msg = models.Message(text=call.data, user=user)
    await msg.save()
    await state.finish()
    if getmsg['Главное меню']['image']:
        match user.lang:
            case 'ru':
                await bot.send_photo(call.from_user.id, getmsg['Главное меню']['image'], getmsg['Главное меню']['ru'], reply_markup=mainmenu)
            case 'en':
                await bot.send_photo(call.from_user.id, getmsg['Главное меню']['image'], getmsg['Главное меню']['en'], reply_markup=mainmenu_en)
    else:
        match user.lang:
            case 'ru':
                await bot.send_message(call.from_user.id, getmsg['Главное меню']['ru'], reply_markup=mainmenu)
            case 'en':
                await bot.send_message(call.from_user.id, getmsg['Главное меню']['en'], reply_markup=mainmenu_en)


@dp.callback_query_handler(text='deposit')
async def dep(call: types.CallbackQuery):
    user = await models.User.get(chat_id=call.from_user.id)
    msg = models.Message(text=call.data, user=user)
    await msg.save()
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    msg = models.Message(text=call.data, user=user)
    wallet = await models.Setting.get(label='Кошелёк').values()
    course = await models.Setting.get(label='Курс').values()
    await msg.save()
    if user.wallet:
        await DepositState.deposit.set()
        match user.lang:
            case 'ru':
                await bot.send_message(call.from_user.id, getmsg['Сумма пополнения']['ru'].format(wallet['value']['usdt'], course['value']['usdt'], wallet['value']['wallet']), parse_mode='Markdown', reply_markup=back_menu)
            case 'en':
                await bot.send_message(call.from_user.id, getmsg['Сумма пополнения']['en'].format(wallet['value']['usdt'], course['value']['usdt'], wallet['value']['wallet']), parse_mode='Markdown', reply_markup=back_menu)
    else:
        await WalletState.wallet.set()
        match user.lang:
            case 'ru':
                await bot.send_message(call.from_user.id, getmsg['Введите кошелёк']['ru'], reply_markup=back_menu)
            case 'en':
                await bot.send_message(call.from_user.id, getmsg['Введите кошелёк']['en'], reply_markup=back_menu)


@dp.callback_query_handler(state=DepositState.deposit, text='back')
async def back_from_dep(call: types.CallbackQuery, state: FSMContext):
    user = await models.User.get(chat_id=call.from_user.id)
    msg = models.Message(text=call.data, user=user)
    await msg.save()
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    msg = models.Message(text=call.data, user=user)
    await msg.save()
    await state.finish()
    if getmsg['Главное меню']['image']:
        match user.lang:
            case 'ru':
                await bot.send_photo(call.from_user.id, getmsg['Главное меню']['image'], getmsg['Главное меню']['ru'], reply_markup=mainmenu)
            case 'en':
                await bot.send_photo(call.from_user.id, getmsg['Главное меню']['image'], getmsg['Главное меню']['en'], reply_markup=mainmenu_en)
    else:
        match user.lang:
            case 'ru':
                await bot.send_message(call.from_user.id, getmsg['Главное меню']['ru'], reply_markup=mainmenu)
            case 'en':
                await bot.send_message(call.from_user.id, getmsg['Главное меню']['en'], reply_markup=mainmenu_en)


@dp.message_handler(state=DepositState.deposit)
async def deposite(message: types.Message, state: FSMContext):
    group = await models.Setting.get(label='Группа').values()
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    user = await models.User.get(chat_id=message.from_user.id)
    msg = models.Message(text=message.text, user=user)
    await msg.save()
    if Decimal(message.text):
        await state.finish()
        match user.lang:
            case 'ru':
                await bot.send_message(message.from_user.id, getmsg['Пополнение успешно']['ru'], reply_markup=back_menu)
            case 'en':
                await bot.send_message(message.from_user.id, getmsg['Пополнение успешно']['en'], reply_markup=back_menu)
        await bot.send_message(group['value']['group_id'], 'Заявка на пополнение:\nНик: @{}\nСумма: {}\n\nПополнение будет проведено автоматически'.format(user.username, Decimal(message.text)))

    else:
        match user.lang:
            case 'ru':
                await bot.send_message(message.from_user.id, getmsg['Неверно пополнение']['ru'], reply_markup=balance_menu)
            case 'en':
                await bot.send_message(message.from_user.id, getmsg['Неверно пополнение']['en'], reply_markup=balance_menu_en)


@dp.callback_query_handler(text='edit')
async def edit(call: types.CallbackQuery):
    user = await models.User.get(chat_id=call.from_user.id)
    msg = models.Message(text=call.data, user=user)
    await msg.save()
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    msg = models.Message(text=call.data, user=user)
    wallet = await models.Setting.get(label='Кошелёк').values()
    await msg.save()
    match user.lang:
        case 'ru':
            await bot.send_message(call.from_user.id, getmsg['Изменить кошелёк']['ru'].format(user.wallet), reply_markup=edit_menu)
        case 'en':
            await bot.send_message(call.from_user.id, getmsg['Изменить кошелёк']['en'].format(user.wallet), reply_markup=edit_menu)
    await EditState.edit.set()


@dp.callback_query_handler(state=EditState.edit, text='back')
async def back_from_edit(call: types.CallbackQuery, state: FSMContext):
    user = await models.User.get(chat_id=call.from_user.id)
    msg = models.Message(text=call.data, user=user)
    await msg.save()
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    msg = models.Message(text=call.data, user=user)
    await msg.save()
    await state.finish()
    if getmsg['Главное меню']['image']:
        match user.lang:
            case 'ru':
                await bot.send_photo(call.from_user.id, getmsg['Главное меню']['image'], getmsg['Главное меню']['ru'], reply_markup=mainmenu)
            case 'en':
                await bot.send_photo(call.from_user.id, getmsg['Главное меню']['image'], getmsg['Главное меню']['en'], reply_markup=mainmenu_en)
    else:
        match user.lang:
            case 'ru':
                await bot.send_message(call.from_user.id, getmsg['Главное меню']['ru'], reply_markup=mainmenu)
            case 'en':
                await bot.send_message(call.from_user.id, getmsg['Главное меню']['en'], reply_markup=mainmenu_en)


@dp.message_handler(state=EditState.edit)
async def editing(message: types.Message, state: FSMContext):
    user = await models.User.get(chat_id=message.from_user.id)
    msg = models.Message(text=message.text, user=user)
    await msg.save()
    getmsg = await models.Setting.all().values()
    imgs = await models.Image.all().values()
    getmsg = format_settings(getmsg, imgs)
    msg = models.Message(text=message.text, user=user)
    await msg.save()
    await state.finish()
    match user.lang:
        case 'en':
            await bot.send_message(message.from_user.id, getmsg['Готово']['en'], reply_markup=mainmenu_en)
            user.wallet = message.text
            await user.save()
        case 'ru':
            await bot.send_message(message.from_user.id, getmsg['Готово']['ru'], reply_markup=mainmenu)
            user.wallet = message.text
            await user.save()


async def run():
    await models.Tortoise.init(db_url="asyncpg://postgres:{}@coupon.localhost:5432".format(os.environ['PASSWORD_DB']), modules={"models": ["models"]})
models.run_async(run())
executor.start_polling(dp)
