import sr# импорт соседнего файла
import tts# импорт соседнего файла
import flask
from flask import request, Flask, abort,send_file
import json
import requests
from flask import send_file
import os
from werkzeug.utils import secure_filename
import cyrtranslit


def translit(s):
    return cyrtranslit.to_latin(s,'ru')


#======================================================================================================================
#логгирование
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='logs_file',
                    filemode='w')
# Until here logs only to file: 'logs_file'

# define a new Handler to log to console as well
console = logging.StreamHandler()
# optional, set the logging level
console.setLevel(logging.INFO)
# set a format which is the same for console use
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

# Now, we can log to both ti file and console
#logging.info('Jackdaws love my big sphinx of quartz.')
#logging.info('Hello world')
#=======================================================================================================================


app=Flask(__name__)
app.config['UPLOAD_PATH'] = ''

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
        print('requests_args below')
        print(request.args)
        message = str(request.args['message']).lower()
        context = get_context(request.args.get('context'))
        state = get_state(request.args.get('state'))
        final_dialog=get_context(request.args.get('final_dialog'))
        confidence=get_context(request.args.get('confidence'))
        id=get_id(request.args.get('id'))
    elif request.method == 'POST':
        print(request.data)
        data = json.loads(request.data.decode('utf-8'))
        message = data['message']
        context = get_context(data.get('context'))
        state = get_state(data.get('state'))
        final_dialog = get_context(request.args.get('final_dialog'))
        confidence = get_context(request.args.get('confidence'))
        id=data['id']
    else:
        abort(400)
    return  message, context,state,final_dialog,confidence,id



def parse_answer(r):
    r= r.json()
    message = r['message']
    context = r['context']
    state = r['state']
    final_dialog = r['final_dialog']
    confidence = r['confidence']
    id=r['id']
    print('message=' + message)
    print('context=' + str(context))
    print('state=' + str(state))
    print('final_dialog=' + str(final_dialog))
    print('confidence=' + str(confidence))
    print('id=' + str(id))
    print('parse_answer: message= ' + message + ' ;context= ' + str(context) + ' ;state= ' + str(
        state) + ' ;final_dialog= ' + str(final_dialog) + ' ;confidence= ' + str(confidence)+' ;id= ' + str(id))
    return message,context,state,final_dialog,confidence,id


def request_from_sr_to_bp(message, context, state, final_dialog, confidence,id):  # отправить запрос на модуль распознавания речи
    print('We send request from sr to bp!!!')
    data = {'message': message, 'context': context, 'state': str(state), 'final_dialog': final_dialog,
            'confidence': str(confidence),'id':str(id)}
    print(data)
    data = json.dumps(data)
    request = 'http://127.0.0.1:8081/voice'
    #request='http://172.29.4.22:8081/voice'
    print('request_from_sr_to_bp= '+request)
    headers = {'content-type': 'application/json'}
    r = requests.post(request,headers=headers, data=data, verify=False)
    #r = requests.post(request, data=data, verify=False)
    print(r.status_code)
    #message, context, state, final_dialog, confidence=parse_answer(r)

    print('We get answer from bp(sr on bp)!!!')
    #return message, context, state, final_dialog, confidence


@app.route("/getSpeech_recognition",methods = ['GET','POST'])# getSpeech_recognition
def getSpeech_recognition():
    print('getSpeech_recognition')
    message, context, state, final_dialog, confidence,id = parse_request()
    answer = sr.just_speech_recognition()
    print('answer_of_sr = '+answer)
    logging.info('answer= '+answer)
    #answer1, context, state, final_dialog, confidence=request_from_sr_to_bp(answer, context, state, final_dialog, confidence)
    #request_from_sr_to_bp(answer, context, state, final_dialog, confidence,id)
    print('getSpeech_recognition send answer!!!')
    return flask.jsonify({'message':answer,'context':context,'state':state,'final_dialog':final_dialog,'confidence':confidence,'id':id})

@app.route("/getTts",methods = ['GET','POST'])# getTTS
def getTts():
    print('getTts')
    message,context,state,final_dialog,confidence,id=parse_request()
    if request.method == 'GET':
        message=request.args['message']
    if request.method == 'POST':
        #print(request.data)
        data = json.loads(request.data.decode('utf-8'))
        message = data['message']
        print('message on tts = '+message)
    answer=tts.just_text_to_speech(message)
    if answer == 0:
        answer = 'Успешно'
    else:
        answer = 'Ошибка'
    logging.info(answer)
    print('getTts worked!!!')
    # return flask.jsonify({'message':answer,'context':context,'state':state,'final_dialog':final_dialog,'confidence':confidence})
    return 'paraparapa'

@app.route('/download_audio', methods=['GET', 'POST'])
def download_audio():
	try:
		return send_file(r'C:\Users\14691412\PycharmProjects\first_serv\s\new12.wav')#ПОМЕНЯТЬ ПУТЬ!!!!!!
	except Exception as e:
		return str(e)

@app.route('/upload_audio', methods=['GET', 'POST'])
def upload_audio():
    if  'sound' in request.files:
        for f in request.files.getlist('sound'):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        return 'Upload completed.'
    return 'gffgfgfgfgf'

from mmk_bot import predict_state_mmk
@app.route("/getSpeech_recognition_new",methods = ['GET','POST'])# getSpeech_recognition(для аудио)
def getSpeech_recognition_new():
    #if 'sound' in request.files:
    #  for f in request.files.getlist('sound'):
     #   filename = secure_filename(f.filename)
     #   f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    #with open("a.wav",'bw') as f:
     ##   chunk_size=4096
       # while True:
          #  chunk=flask.request.stream.read(chunk_size)
            #if len(chunk) == 0:
            #    return
            #f.write(chunk)
    #print(request.get_data())
    #filename = 'newfile.wav'
    #myfile = open(filename, 'wb')
    #myfile.write(request.get_data())
    #myfile.close()
    #print('getSpeech_recognition')
    #message, state = read_message_from_txt()
    #message='dd'
    #state=0
    #context=''
    #final_dialog=0
    #confidence=1
    #id='df'
    #print('We try to recognize next file:'+os.path.join(app.config['UPLOAD_PATH'], filename))
    #answer = sr.just_speech_recognition(mode='audio',path=os.path.join(app.config['UPLOAD_PATH'], filename))
    message, state = read_message_from_txt()
    answer = sr.just_speech_recognition()
    message,state=predict_state_mmk(answer,state,'')
    write_message_to_txt(message, state)
    print('answer_of_sr = '+answer)
    logging.info('answer= '+answer)
    #request_from_sr_to_bp(answer, context, state, final_dialog, confidence,id)

    #answer,state=read_message_from_txt()
    print('getSpeech_recognition send answer!!!')
    #return flask.jsonify({'message':answer,'context':context,'state':state,'final_dialog':final_dialog,'confidence':confidence,'id':id})
    #s=translit(answer)
    #print(s)
    return answer

@app.route("/getTts_new",methods = ['GET','POST'])# getTTS(для аудио)
def getTts_new():
    print('getTts')
    #message,context,state,final_dialog,confidence,id=parse_request()
    #if request.method == 'GET':
     #   message=request.args['message']
    #if request.method == 'POST':
    #    #print(request.data)
    #    data = json.loads(request.data.decode('utf-8'))
    #    message = data['message']
    #    print('message on tts = '+message)
    #message='здрасьте-мордасьте я электронный консультант компании ммк парапарапам'
    message,state=read_message_from_txt()
    answer=tts.just_text_to_speech(message,mode='audio',filename='new_3897.wav')
    print('answer= '+str(answer))
    #request_from_tts_to_skype()
    if answer == 0:
        answer = 'Успешно'
    else:
        answer = 'Ошибка'
    logging.info(answer)
    print('getTts worked!!!')
    # return flask.jsonify({'message':answer,'context':context,'state':state,'final_dialog':final_dialog,'confidence':confidence})
    try:
        return send_file('new_3897.wav')  # ПОМЕНЯТЬ ПУТЬ!!!!!!
    except Exception as e:
        return str(e)



def request_from_tts_to_skype():
    file = open('1.mp3', 'rb')
    response = requests.post("http://127.0.0.1:3897/upload_audio", files={'sound': file}, verify=False)
    file.close()


def read_message_from_txt():
    separator = "="
    keys = {}
    with open(r'C:\Users\ДНС\Desktop\sr_tts_flask\mess.txt') as f:
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
#main('привет','raupov2')

app.run(host='127.0.0.1',debug=True,port=9092)
#app.run()