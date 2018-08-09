from pygame import mixer
import time
from gtts import gTTS
from yandex_speech import TTS


import os

path_to_sr_tts_flask=os.getcwd()
path_to_resources=os.path.join(path_to_sr_tts_flask,'resources')
path_to_balcon=os.path.join(path_to_resources,'balcon')


########################################################################################################################
#                                              1 TEXT-TO-SPEECH


def just_text_to_speech(phrase,mode='',filename='speech.mp3'): # преобразование текста в речь (внутри Гугл)
        try:
            tts = gTTS(text=phrase, lang="ru")
            #tts.speed=1
            tts.save(filename)
        except Exception as e:
            print("[GoogleTTS] Не удалось синтезировать речь: {0}".format(e))
            return 1
        if mode == 'audio':
            return 0 #filename
        else:

            mixer.init(25000)
            mixer.music.load(filename)
            mixer.music.play()
            while mixer.music.get_busy():
                time.sleep(0.1)
            mixer.music.stop()
            mixer.music.load('new.waw')# нужен второй аудио файл, иначе миксер валится из-за permission error!!!

        return 0


def just_yandex_tts(text): # синтез речи от Яндекс SpeechCloud (Технологии Яндекса)
    try:
        tts = TTS("oksana", "mp3", "60a2b005-738e-42b6-8b78-9ee9b7d57031",speed=1.2)# если не работает, то нужно получить и указать свой ключ от Яндекс SpeechCloud
        tts.generate(text)#можно менять скорость
        tts.save('speechY.mp3')
    except Exception as e:
        print("[YandexTTS] Не удалось синтезировать речь: {0}".format(e))
        return

    mixer.init()
    mixer.music.load('speechY.mp3')
    mixer.music.play()
    while mixer.music.get_busy():
        time.sleep(0.1)
    mixer.music.stop()
    mixer.music.load('new.waw')# нужен второй аудио файл, иначе миксер валится из-за permission error!!!




def balabolka_tts(text): # синтез речи оффлайн от балаболки(нужно установить RHVoice от Ольги Яковлевой!!!)
    #не уверен, что это будет работать на линуксе - надо проверять
    s=path_to_balcon + '''\\balcon -n "RHVoice RHVoice Elena (Russian)" -t "''' + text + '''"'''
    print(s)
    a=os.system(s)
    return a






