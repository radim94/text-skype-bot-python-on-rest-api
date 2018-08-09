#======================================================================================================================
#====================================== ИМПОРТ БИБЛИОТЕК,ОПИСАНИЕ ПЕРЕМЕННЫХ ==========================================

from sr import just_speech_recognition
import uuid
from flask import Flask, request,abort
import requests
import json
from mmk_bot import predict_state_mmk_flask
r = 0
callback_uri = 'https://466d45ec.ngrok.io/api/calling/callback'# адрес колбэка
file_uri = 'https://b11bf0ff.ngrok.io/getTts_new'#адрес, откуда будет браться речь бота

app = Flask(__name__)
app.config['UPLOAD_PATH'] = ''
# фиктивные данные для полей сообщение, кнтекст, сотсояние  и т.д.
message=''
context=''
state=0
final_dialog=0
confidence=1
id='a'

#данные бота Microsoft Bot Framework
CLIENT_ID ="ff5ef026-e21e-4e93-a135-daacd99272ac"
CLIENT_SECRET ="owtlyhQKESN3774)_=aCR3@"

########################################################################################################################
########################################################################################################################
#                                                  1 ГОЛОСОВОЙ ЗВОНОК

def get_message(): # логика обработки голосового звонка
    print('get_message')
    global r;
    print(r)
    if r%2==0: #r==2:#r%2==0:
        data=play_tts()
        print('data=play tts')
        return data
    else: #elif r==3:
        data=record()
        print('data=record')
        return data

@app.route("/api/calling/call",methods = ['GET','POST'])# call
def call():
    print('Call')
    global r;
    r=r+1
    data = json.loads(request.data.decode('utf-8'))
    print('Call data input')
    print(data)
    data = answer()
    print('Call data output')
    print(data)
    return data


@app.route("/api/calling/callback", methods = ['GET', 'POST'])# callback
def callback():
    print('Callback')
    global r;
    r = r + 1
    print(r)
    if (r==2)|(r%2==1):#(r==2)|(r==3):#
        data = json.loads(request.data.decode('utf-8'))
        print('Callback data input')
        print(data)
    else:#elif(r==4): #else
        filename = 'newfile1112.wav'
        f = request.get_data()
        with open(filename, 'wb') as file:
            pos = f.find(b'RIFF')
            file.write(f[pos:])
        print('File is written!!!')
        asd = just_speech_recognition(path=filename,mode='audio')
        print(asd)
        #response = request_to_getSpeechrecognition(message, context, state, final_dialog, confidence, id)
        print('Response from sr')
    data = get_message()
    print(data)
    print('Callback data output')
    return data  # 'парапарапарапам'

#record and play

def r_a(): # вспомогательная функция, чтобы не кэшировался запрос на tts
    s=str(uuid.uuid4())
    print(s)
    return s

def play_tts():#bot send request on callback to play tts
    print('Play TTS')
    data = {
  "links": {
    "callback": callback_uri
  },
  "actions": [
    {
      "operationId": "d18e7f63-0400-48ff-964b-302cf4910dd3",
      "action": "playPrompt",
      "prompts": [
        {
          "fileUri": file_uri+'?message='+r_a()
        }
      ]
    }
  ],
  "notificationSubscriptions": [
    "callStateChange"
  ]
}
    data=json.dumps(data)
    return data



def record():# bot send request on record for client speech
    print('Record')
    data = {
  "links": {
    "callback": callback_uri
  },
  "actions": [
    {
      "operationId": "efe617d7-4de5-42e9-b4e1-90dfd5850e49",
      "action": "record",
      "maxDurationInSeconds": 10,
     "initialSilenceTimeoutInSeconds": 5,
      "maxSilenceTimeoutInSeconds": 5,
      "playBeep": True,
        "recordingFormat": 'wav',
    }
  ],
  "notificationSubscriptions": [
    "callStateChange"
  ]
    }

    data = json.dumps(data)
    return data

def answer():#answer
    print('Request on answer2')
    data={
  "links": {
    "callback": callback_uri
  },
  "actions": [
    {
      "operationId": "673048f9-4442-440b-93a3-faa7433c977a",
      "action": "answer",
      "acceptModalityTypes": [
        "audio"
      ]
    }
  ],
  "notificationSubscriptions": [
    "callStateChange"
  ]
}
    data=json.dumps(data)
    return data


def answer_with_propmpt():#answer+prompt
    print('Request on answer2')
    data={
  "links": {
    "callback": callback_uri
  },
  "actions": [
    {
      "operationId": "673048f9-4442-440b-93a3-faa7433c977a",
      "action": "answer",
      "acceptModalityTypes": [
        "audio"
      ]
    },
    {
      "operationId": "030eeb97-8210-48fd-b497-d761154f0b5a",
      "action": "playPrompt",
      "prompts": [
        {
          "value": "Welcome to test bot",
          "voice": "male"
        }
      ]
    }
  ],
  "notificationSubscriptions": [
    "callStateChange"
  ]
}
    data=json.dumps(data)
    return data



def hangup():# bot send request on hangup
    print('Request on hangup')
    data={
  "links": {
    "callback": callback_uri
  },
  "actions": [
    {
      "operationId": "d2cb708e-f8ab-4aa1-bcf6-b9396afe4b70",
      "action": "hangup"
    }
  ],
  "notificationSubscriptions": [
    "callStateChange"
  ]
}
    data=json.dumps(data)
    return data

########################################################################################################################
########################################################################################################################
#                       2 TEXT PART(MESSAGES CONTROLLER)



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



@app.route('/api/messages', methods=['GET', 'POST'])#рут для контроля сообщений
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
    answer=handle_dialog(message)
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
    "text": answer,
    "replyToId": activity_id
    }
    data = json.dumps(msg)
    TOKEN = get_access_token(CLIENT_ID, CLIENT_SECRET)
    print(TOKEN)
    if TOKEN:
        print(send_message_new(TOKEN, conversation_id, activity_id, data))
    return 'парапарапарапам'

def handle_dialog(message): # обработка сообщения(вызываем логику бота для ответа сообщением на сообщение в скайпе)
    print('handle_dialog')
    context = ''
    m,state=read_message_from_txt()
    if state==8:
        state=0
    answer,context,state=predict_state_mmk_flask(message,state,context)
    print("answer="+answer+" state="+str(state))
    write_message_to_txt(answer, state)
    return answer



########################################################################################################################
########################################################################################################################
#                                           3 ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ

def read_message_from_txt():
    separator = "="
    keys = {}
    with open(r'mess.txt') as f:
        for line in f:
            if separator in line:
                # Find the name and value by splitting the string
                name, value = line.split(separator, 1)

                # Assign key value pair to dict
                # strip() removes white space from the ends of strings
                keys[name.strip()] = value.strip()
        message=str(keys['message'])
        state=int(keys['state'])
    return message,state


def write_message_to_txt(message:str, state:int):
    with open('mess.txt', 'w') as file_2: # Путь  и имя нового файла
        file_2.write('message='+str(message)+'\nstate='+str(state)) # Записываем все что в переменной в новый файл


def request_to_getSpeechrecognition(message, context, state, final_dialog, confidence,id): # запрос на распознавание речи
    print('request to get speech recognition')
    data = {'message': message, 'context': context, 'state': str(state), 'final_dialog': final_dialog,
            'confidence': str(confidence),'id':str(id)}
    data = json.dumps(data)
    request = 'http://127.0.0.1:9092/getSpeech_recognition_new'
    ###################################################################################################################
    #file = open('1.mp3', 'rb')#ПОМЕНЯТЬ ПУТИ!!! ВОЗМОЖНО, ОШИБКА!!!!!
    #response = requests.post('http://127.0.0.1:9092/getSpeech_recognition_new', files={'sound': file,'data':data}, verify=False)
    response = requests.post('http://127.0.0.1:9092/getSpeech_recognition_new', data=data, verify=False)
    #file.close()
    ###################################################################################################################
    return response

def request_to_tts(message, context, state, final_dialog, confidence,id): # запрос на синтез речи
    data = {'message': message, 'context': context, 'state': str(state), 'final_dialog': final_dialog,
            'confidence': str(confidence),'id':str(id)}
    data = json.dumps(data)
    request = 'http://127.0.0.1:9092/getTts_new'
    r = requests.post(request, data=data, verify=False)
    return r

def parse_answer(r): #парсим Response запроса  модуля requests
    data=r.json()
    message = data['message']
    state = data['state']
    context = data['context']
    final_dialog = data['final_dialog']
    confidence = data['confidence']
    id=data['id']
    print('parse_answer: message= ' + message + ' ;context= ' + str(context) + ' ;state= ' + str(state) + ' ;final_dialog= ' + str(final_dialog) + ' ;confidence= ' + str(confidence)+' ;id= '+str(id))
    return message,context,state,final_dialog,confidence,id


def get_context(context=None):# получаем контекст
    if (context==None):
        context=''
    return context

def get_state(state=None):# получаем состояние
    if (state==None):
        state=0
    return int(state)

def get_final_dialog(final_dialog=None):# получаем информацию, конечное состояние или нет
    if (final_dialog==None):
        final_dialog='False'
    return final_dialog

def get_confidence(confidence=None):# получаем вероятность состояния
    if (confidence==None):
        confidence=1
    return confidence

def get_id(id=None):# получаем вероятность состояния
    if (id==None):
        id='0'
    return id

def parse_request(): # получить данные из запроса
    if request.method == 'GET':
        print('request_args below')
        print(request.args)
        message = str(request.args['message']).lower()
        context = get_context(request.args.get('context'))
        state = get_state(request.args.get('state'))
    elif request.method == 'POST':
        print('request_data below')
        print(request.data)
        data = json.loads(request.data.decode('utf-8'))
        message = data['message']
        context = get_context(data.get('context'))
        state = get_state(data.get('state'))
    else:
        abort(400)
    return  message, context,state

########################################################################################################################
########################################################################################################################
#                                                                MAIN

app.run(port=9090)