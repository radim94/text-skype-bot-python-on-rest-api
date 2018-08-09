#!/usr/bin/env python
import requests
import json
from flask import Flask,request,jsonify

#from config.cfg import SKYPE_CLIENT_ID, SKYPE_CLIENT_SECRET

#CLIENT_ID = 'ff5ef026-e21e-4e93-a135-daacd99272ac'
#CLIENT_SECRET = 'owtlyhQKESN3774)_=aCR3@'

CLIENT_ID ="ff5ef026-e21e-4e93-a135-daacd99272ac"
CLIENT_SECRET ="owtlyhQKESN3774)_=aCR3@"

def get_access_token(client_id, client_secret):
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


def send_message(token, skype_id, message, type):
    if type == 'direct':
        URL = "https://apis.skype.com/v2/conversations/8:{}/activities".format(skype_id)
    if type == 'chat':
        URL = "https://apis.skype.com/v2/conversations/19:{}/activities".format(skype_id)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token
    }
    data = json.dumps(dict(message=dict(content=message))).encode()
    r = requests.post(URL, data=data, headers=headers)
    return r.text, r.status_code

#=======================================================================================================================

def send_message_new(token, conversation_id, activity_id, data):
    URL = "https://smba.trafficmanager.net/apis/v3/conversations/%s/activities/%s" % (conversation_id,activity_id)
    print(URL)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token
    }
    #data = json.dumps(dict(message=dict(content=message))).encode()
    r = requests.post(URL, data=data, headers=headers)
    return r.text, r.status_code


def main(message, skype_id):
    TOKEN = get_access_token(CLIENT_ID, CLIENT_SECRET)
    print(TOKEN)
    if TOKEN:
        #conversation_type = 'chat' if 'thread.skype' in skype_id else 'direct'
        print(send_message(TOKEN, skype_id, message,'direct'))
        #return send_message(TOKEN, skype_id, message, conversation_type)



app = Flask(__name__)

@app.route('/api/messages', methods=['GET', 'POST'])
def main_new():
    data = json.loads(request.data.decode('utf-8'))
    print(data)
    message = data['text']
    conversation_id=data['conversation']['id']# id беседы
    #conversation_name = data['conversation']['name']
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
        "id": conversation_id#,
       # "name": conversation_name
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
        print(send_message_new(TOKEN, conversation_id, activity_id, data))
    return 'парапарапарапам'


#main('привет','raupov2')
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3897)# ssl_contex389t=context