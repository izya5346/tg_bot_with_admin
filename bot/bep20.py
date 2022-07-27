from bscscan import BscScan
import asyncio
from decimal import Decimal
import models
# from config import bot
import time
from datetime import timedelta
from tortoise.exceptions import DoesNotExist
import os
API_KEY = 'QQFIKSIUM341UYDQ7UBFI96ZYHR8PD3GID'
CONTRACT_ADDRESS = '0xA201E694f3FBbf5445F16596380d0f6f105Cb265'
USDT_ADDRESS = '0x55d398326f99059ff775485246999027b3197955'
BUSD_ADDRESS = '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56'
async def run():
    await models.Tortoise.init(db_url="asyncpg://postgres:{}@coupon.localhost:5432".format(os.environ['PASSWORD_DB']), modules={"models": ["models"]})
    # sett = models.Setting(label = 'Группа', value = {'group_id': '-763088834', 'datetime': datetime.now().strftime('%H:%M %d.%m.%Y')})
    # await sett.save()

async def lbl():
    wallet = await models.Setting.get(label = 'Кошелёк').values()
    async with BscScan(API_KEY) as bsc:
        try:
            da = await bsc.get_bep20_token_transfer_events_by_address_and_contract_paginated(contract_address = CONTRACT_ADDRESS, address=wallet['value']['lbl'].lower(), page = 1, offset = 20, sort='asc')
            for data in da:
                if data['to'] == wallet['value']['lbl'].lower():
                    status = await bsc.get_tx_receipt_status(data['hash'])
                    if status['status']:
                        tx, created = await models.Transaction.get_or_create(hash = data['hash'])
                        if created:
                            try:
                                user = await models.User.get(wallet = data['from'])
                                user.balance+= Decimal(data['value']) / 1000
                                await user.save()
                                hs = models.History(type='in', amount=Decimal(data['value']) / 1000, user=user)
                                await hs.save()
                            except DoesNotExist:
                                pass
        except AssertionError:
            pass
async def usdt():
    wallet = await models.Setting.get(label = 'Кошелёк').values()
    course = await models.Setting.get(label = 'Курс').values()
    async with BscScan(API_KEY) as bsc:
        try:
            da = await bsc.get_bep20_token_transfer_events_by_address_and_contract_paginated(contract_address = USDT_ADDRESS, address=wallet['value']['usdt'].lower(), page = 1, offset = 20, sort='asc')
            for data in da:
                if data['to'] == wallet['value']['usdt'].lower():
                    status = await bsc.get_tx_receipt_status(data['hash'])
                    if status['status']:
                        tx, created = await models.Transaction.get_or_create(hash = data['hash'])
                        if created:
                            try:
                                user = await models.User.get(wallet = data['from'])
                                user.balance+= Decimal(data['value']) / 10 ** 18 / Decimal(course['usdt'])
                                await user.save()
                                hs = models.History(type='in', amount=Decimal(data['value']) / 10 ** 18 / Decimal(course['usdt']), user=user)
                                await hs.save()
                            except DoesNotExist:
                                pass
        except AssertionError:
            pass
async def busd():
    wallet = await models.Setting.get(label = 'Кошелёк').values()
    course = await models.Setting.get(label = 'Курс').values()
    async with BscScan(API_KEY) as bsc:
        try:
            da = await bsc.get_bep20_token_transfer_events_by_address_and_contract_paginated(contract_address = BUSD_ADDRESS, address=wallet['value']['usdt'].lower(), page = 1, offset = 20, sort='asc')
            for data in da:
                if data['to'] == wallet['value']['usdt'].lower():
                    status = await bsc.get_tx_receipt_status(data['hash'])
                    if status['status']:
                        tx, created = await models.Transaction.get_or_create(hash = data['hash'])
                        if created:
                            try:
                                user = await models.User.get(wallet = data['from'])
                                user.balance+= Decimal(data['value']) / 10 ** 18 / Decimal(course['usdt'])
                                await user.save()
                                hs = models.History(type='in', amount=Decimal(data['value']) / 10 ** 18 / Decimal(course['usdt']), user=user)
                                await hs.save()
                            except DoesNotExist:
                                pass
        except AssertionError:
            pass
async def runn():
    while True:
        await asyncio.gather(lbl())
        await asyncio.gather(usdt())
        await asyncio.gather(busd())
        await asyncio.sleep(timedelta(seconds=10).seconds)

if __name__ == "__main__":
    models.run_async(run())
    asyncio.run(runn())

