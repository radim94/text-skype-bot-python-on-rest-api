#!/usr/bin/env python
import requests
import json
from flask import Flask,request

CLIENT_ID ="ff5ef026-e21e-4e93-a135-daacd99272ac"
CLIENT_SECRET ="owtlyhQKESN3774)_=aCR3@"

def get_access_token(client_id, client_secret):# получаем токен доступа
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://api.botframework.com/.default',
        'grant_type': 'client_credentials'
    }
    r = requests.post("https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token", data=payload,
                      headers={'Content-Type': 'application/x-www-form-urlencoded'})
    try:
        response = json.loads(r.text)
        return response['access_token']
    except:
        return False



def send_message(token, conversation_id, activity_id, data):#отправляем сообщение
    URL = "https://smba.trafficmanager.net/apis/v3/conversations/%s/activities/%s" % (conversation_id,activity_id)
    print(URL)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token
    }
    r = requests.post(URL, data=data, headers=headers)
    return r.text, r.status_code


app = Flask(__name__)

@app.route('/api/messages', methods=['GET', 'POST'])
def main():
    data = json.loads(request.data.decode('utf-8'))
    print(data)
    message = data['text']
    conversation_id=data['conversation']['id']# id беседы
    type=data['type']# тип активности(сообщение, голосовой звонок и т.д.)
    recipient_id=data['from']['id']#от кого получили сообщение и кому будем отвечать
    recipient_name = data['from']['name']
    from_id=data['recipient']['id']# имя и id бота
    from_name=data['recipient']['name']
    activity_id=data['id']# id активности(сообщения, голосового звонка и т.д.)

    msg = {
    "type": type,
    "from": {
        "id": from_id,
        "name": from_name
    },
    "conversation": {
        "id": conversation_id
   },
   "recipient": {
        "id": recipient_id,
        "name": recipient_name
    },
    "text": "I received this message:"+ message,
    "replyToId": activity_id
    }
    data = json.dumps(msg)
    TOKEN = get_access_token(CLIENT_ID, CLIENT_SECRET)
    print(TOKEN)
    if TOKEN:
        print(send_message(TOKEN, conversation_id, activity_id, data))
    return 'парапарапарапам'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3897)