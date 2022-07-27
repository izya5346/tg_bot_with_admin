from fileinput import filename
import json
from fastapi import FastAPI, Form, Request, File, UploadFile
from tortoise.contrib.fastapi import register_tortoise
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
from models import *
from datetime import datetime, time
import pandas as pd
import os
import logging
import secrets
from bot import *
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import aiofiles
security = HTTPBasic()
logging.basicConfig(filename='site.log', filemode='w',level=logging.DEBUG)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "Vasy")
    correct_password = secrets.compare_digest(credentials.password, "Suslik")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get('/')
async def index(request: Request, nick: str = Depends(get_current_username)):
    return RedirectResponse('/messages')


@app.get('/messages', response_class=HTMLResponse)
async def messages(request: Request, nick: str = Depends(get_current_username)):
    data = Message.all().prefetch_related('user').order_by(
        '-date').values('id', 'date', 'text', username='user__username')
    new = []
    async for i in data:
        date = i.pop('date')
        i.update({'date': date.strftime('%H:%M %d.%m.%Y')})
        new.append(i)
    return templates.TemplateResponse("index1.html", {"request": request, "messages": new, "action": "messages"})


@app.post('/coupons', response_class=HTMLResponse)
@app.get('/coupons', response_class=HTMLResponse)
async def coupons(request: Request, nick: str = Depends(get_current_username)):
    data = Coupon.all().prefetch_related('user').order_by('-date').values('id',
                                                                          'arr', 'is_loaded', 'date', username='user__username')
    now = datetime.today().strftime('%Y-%m-%d')
    new = []
    async for i in data:
        coup = i['arr'].pop('coupon')
        _ = i.pop('arr')
        i.update({'coupon': ' '.join(coup)})
        date = i.pop('date')
        i.update({'date': date.strftime('%H:%M %d.%m.%Y')})
        new.append(i)
    return templates.TemplateResponse("index1.html", {"request": request, "coupons": new, "action": "coupons", 'now': now})


@app.post('/users', response_class=HTMLResponse)
@app.get('/users', response_class=HTMLResponse)
async def users(request: Request, nick: str = Depends(get_current_username)):
    data = User.all().order_by('-id').values('id', 'username', 'balance',
                                             'refcode', 'count_refs', 'count_refs_2nd', 'wallet')
    new = []
    async for i in data:
        user1 = await User.filter(refered_by=i['refcode']).values()
        if user1:
            for j in user1:
                i.update({'refs1': []})
                i['refs1'].append(j['username'])
                user2 = await User.filter(refered_by=j['refcode']).values()
                if user2:
                    for k in user2:
                        i.update({'refs2': []})
                        i['refs2'].append(k['username'])
        new.append(i)
    return templates.TemplateResponse("index1.html", {"request": request, "users": new, "action": "users"})


@app.get('/{action}/edit/{id}', response_class=HTMLResponse)
async def edit(request: Request, action: str, id: str, nick: str = Depends(get_current_username)):
    if action == 'users':
        data = await User.get(id=id).values('balance', 'username', 'id', 'wallet')
        return templates.TemplateResponse("form.html", {"request": request, "user": data, "action": action})
    elif action == 'settings.msgs':
        data = await Setting.get(id=id).values()
        return templates.TemplateResponse("form.html", {"request": request, "setting": data, "action": action})
    elif action == 'settings':
        data = await Setting.get(id=id).values()
        data['value'] = json.dumps(data['value'], ensure_ascii=False)
        return templates.TemplateResponse("form.html", {"request": request, "setting": data, "action": action})


@app.post('/users/save')
async def save_user(request: Request, balance: str = Form(), username: str = Form(), id: str = Form(), wallet: str = Form(), nick: str = Depends(get_current_username)):
    user = await User.get(id=id)
    user.balance = balance
    user.wallet = wallet
    await user.save()
    return RedirectResponse('/users')


@app.post('/settings.msgs/save')
async def save_msgs(request: Request, image: UploadFile = File(None), en: str = Form(), ru: str = Form(), id: str = Form(), nick: str = Depends(get_current_username)):
    settings = await Setting.get(id=id)
    pic = await image.read()
    if len(pic) > 0:
        message = await bot.send_photo('357536913', pic, reply_markup = back_menu, disable_notification = True)
        img = Image(filename = image.filename, file_id = message.photo[-1].file_id, message = settings)
        await img.save()
        async with aiofiles.open('./static/images/{}'.format(image.filename), 'wb') as f:
            await f.write(pic)
    settings.value.update({'message': {'ru': ru, 'en': en}})
    await settings.save()
    return RedirectResponse('/settings')


@app.post('/settings/save')
async def save_settings(request: Request, value: str = Form(), id: str = Form(), nick: str = Depends(get_current_username)):
    settings = await Setting.get(id=id)
    if "'" in value:
        value = value.replace("'", '"')
    settings.value = json.loads(value)
    await settings.save()
    return RedirectResponse('/settings')


@app.get('/load')
async def load(request: Request, nick: str = Depends(get_current_username)):
    data = await Coupon.filter(is_loaded=False).order_by(
        '-id').prefetch_related('user').values('arr', 'date', username='user__username')
    await Coupon.filter(is_loaded=False).update(is_loaded=True)
    for j in os.listdir():
        if '.xlsx' in j:
            os.remove(j)
    new = []
    for i in data:
        coup = i['arr'].pop('coupon')
        _ = i.pop('arr')
        i.update({'coupon': ' '.join(coup)})
        date = i.pop('date')
        i.update({'date': date.strftime('%H:%M %d.%m.%Y')})
        new.append(i)
    df = pd.DataFrame(data=new)
    filename = datetime.now().strftime('%H:%M %d.%m.%Y') + '.xlsx'
    df.to_excel(filename, index=False)
    return FileResponse(filename, media_type='application/octet-stream', filename=filename)


@app.get('/loadmsg')
async def loadmsg(request: Request, nick: str = Depends(get_current_username)):
    data = Message.all().prefetch_related('user').order_by(
        '-id').values(
        'date', 'text', username='user__username')
    for j in os.listdir():
        if '.xlsx' in j:
            os.remove(j)
    new = []
    async for i in data:
        date = i.pop('date')
        i.update({'date': date.strftime('%H:%M %d.%m.%Y')})
        new.append(i)
    df = pd.DataFrame(data=new)
    filename = datetime.now().strftime('%H:%M %d.%m.%Y') + '.xlsx'
    df.to_excel(filename, index=False)
    return FileResponse(filename, media_type='application/octet-stream', filename=filename)


@app.post('/settings', response_class=HTMLResponse)
@app.get('/settings', response_class=HTMLResponse)
async def settings(request: Request, nick: str = Depends(get_current_username)):
    data = Setting.all().order_by('-id').values()
    # imgs = await Image.all().order_by('-id').values()
    msgs = []
    other = []
    async for i in data:
        if list(i['value'].keys())[0] == 'message':
            img = await Image.filter(message = i['id'])
            if img:
                i.update({'image': img[-1].filename})
            msgs.append(i)
        else:
            other.append(i)
    return templates.TemplateResponse("settings.html", {"request": request, "msgs": msgs, "other": other, "action": "settings"})


@app.get('/history', response_class=HTMLResponse)
async def history(request: Request, nick: str = Depends(get_current_username)):
    data = History.all().order_by('-date').prefetch_related('user').values('id',
                                                                           'date', 'type', 'amount', username='user__username')
    new = []
    async for i in data:
        date = i.pop('date')
        i.update({'date': date.strftime('%H:%M %d.%m.%Y')})
        new.append(i)
    return templates.TemplateResponse("index1.html", {"request": request, "history": new, "action": "history"})


@app.get('/loadhist', response_class=HTMLResponse)
async def loadhist(request: Request, nick: str = Depends(get_current_username)):
    data = History.all().order_by('-date').prefetch_related('user').values('date',
                                                                           'type', 'amount', username='user__username')
    for j in os.listdir():
        if '.xlsx' in j:
            os.remove(j)
    new = []
    async for i in data:
        date = i.pop('date')
        i.update({'date': date.strftime('%H:%M %d.%m.%Y')})
        new.append(i)
    df = pd.DataFrame(data=new)
    filename = datetime.now().strftime('%H:%M %d.%m.%Y') + '.xlsx'
    df.to_excel(filename, index=False)
    return FileResponse(filename, media_type='application/octet-stream', filename=filename)


@app.post('/delcoups')
async def delcoups(request: Request, dat: str = Form(), nick: str = Depends(get_current_username)):
    dat = datetime.strptime(dat, '%Y-%m-%d')
    tim = time(23, 59)
    dat = datetime.combine(date=dat, time=tim)
    data = Coupon.filter(date__lte=dat)
    await data.delete()
    return RedirectResponse('/coupons')


@app.post('/write2person', response_class=HTMLResponse)
@app.get('/write2person', response_class=HTMLResponse)
async def write_to_person(request: Request, nick: str = Depends(get_current_username)):
    data = await User.all().values('id', 'username')
    return templates.TemplateResponse("form.html", {"request": request, "data": data, "action": 'write2person'})


@app.post('/do_mailing', response_class=HTMLResponse)
@app.get('/do_mailing', response_class=HTMLResponse)
async def do_mailing(request: Request, nick: str = Depends(get_current_username)):
    return templates.TemplateResponse("form.html", {"request": request, "action": 'do_mailing'})


@app.post('/write2person/send', response_class=HTMLResponse)
async def send_to_person(request: Request, user: str = Form(), message: str = Form(), nick: str = Depends(get_current_username)):
    user = await User.get(id=user)
    await bot.send_message(user.chat_id, message, reply_markup=back_menu)
    return RedirectResponse('/write2person')


@app.post('/do_mailing/send', response_class=HTMLResponse)
async def send_mailing(request: Request, message: str = Form(), image: UploadFile = File(None), lang:str = Form(), nick: str = Depends(get_current_username)):
    users = User.filter(lang = lang)
    pic = await image.read()
    async for user in users:
        try:
            if len(pic) > 0:
                await bot.send_photo(user.chat_id, pic, message,reply_markup = back_menu)
            else:
                await bot.send_message(user.chat_id, message, reply_markup=back_menu)
        except BotBlocked:
            ...
    return RedirectResponse('/do_mailing')

register_tortoise(app, db_url='asyncpg://postgres:{}@coupon.localhost:5432'.format(os.environ['PASSWORD_DB']),
                  modules={"models": ["models"]}, generate_schemas=True)
