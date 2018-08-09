from speech_recognition import WaitTimeoutError
import speech_recognition as sr

import requests
import pyaudio
import wave
import xml.etree.ElementTree as ET
########################################################################################################################
#                                              1 SPEECH RECOGNITION PART


r = sr.Recognizer()



def just_speech_recognition(mode='',path='',frames=None):# распознавание речи (внутри по умолчанию зашит Гугл, можно менять на некоторые другие голосовые движки)
    global r
    if mode=='audio':
        print('audiofile')
        with sr.AudioFile(path) as source:
            print("Скажите что-нибудь")
            audio=123
            try:
                #audio = r.listen(source,timeout=5,phrase_time_limit=10)
                audio=r.record(source)
            except WaitTimeoutError as e:
                s='Пожалуйста,не молчите!'
                print("Ошибка ожидания; {0}".format(e))
    elif mode=='audiodata':
        print('audiodata')
        with sr.AudioFile(frames) as source:
            print("Скажите что-нибудь")
            audio=123
            try:
                audio = r.record(source)
            except WaitTimeoutError as e:
                s='Пожалуйста,не молчите!'
                print("Ошибка ожидания; {0}".format(e))
    else:
        print('microphone')
        with sr.Microphone() as source:
            print("Скажите что-нибудь")
            audio=123
            try:
                #audio = r.record(source)
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
            except WaitTimeoutError as e:
                s='Пожалуйста,не молчите!'
                print("Ошибка ожидания; {0}".format(e))
    try:
        s=r.recognize_google(audio, language="ru-RU")
        print(s)
    except sr.UnknownValueError as e:
        s="Робот не расслышал фразу"
        print("Робот не расслышал фразу; {0}".format(e))
    except sr.RequestError as e:
        s="Ошибка сервиса"
        print("Ошибка сервиса; {0}".format(e))
        r = sr.Recognizer()
    except AssertionError as e:
        s = "Пожалуйста, не молчите!"
        print("Ошибка ожидания; {0}".format(e))
    return s

def record(): # вспомогательная функция записи в mp3 для just_alisa_sr()
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 16000
    CHUNK = 1024
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "file.mp3"

    audio = pyaudio.PyAudio()

    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("recording...")
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("finished recording")

    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()



def just_yandex_sr(): # распознавание речи от Яндекс SpeechCloud (Технологии Яндекса)
    # asr.yandex.net/asr_xml?key=API-ключ&uuid=UUID&topic=queries&lang=ru-RU"
    record()# сначала, записываем в mp3 речь клиента, затем  отправляем post запрос на Яндекс
    #path_to_audio="file.mp3"#r'C:\Users\14691412\contact-center-bot\src\python\speech.mp3'
    path_to_audio='new.mp3'
    url = 'http://asr.yandex.net/asr_xml?uuid=01ae13cb744628b58fb536c496dab1e7&key=60a2b005-738e-42b6-8b78-9ee9b7d57031&topic=queries'
    # нужно указать уникальный uuid (рандомно генерируется на стороне пользователя) и key - получаем у Яндекса( надо регаться для использования сервиса)
    # подробнее можно почитать здесь https://tech.yandex.ru/speechkit/cloud/doc/guide/concepts/speechkit-cloud-about-docpage/
    files = {'file': open(path_to_audio, 'rb')}
    headers = {'host': 'asr.yandex.net', 'content-type': 'audio/x-mpeg-3'}#'audio/x-mpeg-3'
    r = requests.post(url, files=files, headers=headers, verify=False)
    print(r)
    print(r.text)
    tree = ET.fromstring(r.text)
    answer = tree.find('variant').text #POST - запрос возвращает строку в виде xml. Оттуда достаём с помощью xml-парсера нужный нам ответ
    return answer


