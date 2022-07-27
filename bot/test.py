import aiogram
import models
import asyncio
from config import *
from datetime import datetime
import os
async def run():
    await models.Tortoise.init(db_url="asyncpg://postgres:{}@coupon.localhost:5432".format(os.environ['PASSWORD_DB']), modules={"models": ["models"]})
    sett = models.Setting(id = 27, label = 'Изменить кошелёк', value = {'message': {'ru': 'Ваш текущий кошелёк: {}\nВведите кошелёк в сети bep20 или нажмите назад', 'en': 'Your current wallet: {}\nEnter a wallet in the bep20 network or click back'}})
    await sett.save()
    # print('0xEe2D6a946cfC72a892331cfD132AE7B9133eFBC8'.lower())
models.run_async(run())
# async def send():
#     await bot.send_message('-763088834', 'Test')
# asyncio.run(send())