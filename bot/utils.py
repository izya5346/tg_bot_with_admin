def check_coupon(st: str):
    arr = st.split()
    if len(arr) == 6:
        booltmp = True
        for i in arr:
            booltmp*= int(i) in range(1, 46)
        return booltmp, arr
    else:
        return False, arr
def last_image(d: list[dict], id):
    mx = 0
    image = None
    for i in d:
        if i['message_id'] == id:
            if i['id'] > mx:
                mx = i['id']
                image = i['file_id']
    return image
def format_settings(d: list[dict], dd: list[dict]) -> dict:
    new = {}
    for i in d:
        if list(i['value'].keys())[0] == 'message':
            new.update({i['label']: i['value']['message']})
            new[i['label']].update({'image':last_image(dd, i['id'])})
    return new

