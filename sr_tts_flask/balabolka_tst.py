import os

path_to_sr_tts_flask=os.getcwd()
path_to_resources=os.path.join(path_to_sr_tts_flask,'resources')
path_to_balcon=os.path.join(path_to_resources,'balcon')

def balabolka_tts(text):
    s=path_to_balcon + '''\\balcon -n "RHVoice RHVoice Elena (Russian)" -t "''' + text + '''"'''
    print(s)
    a=os.system(s)
    return a

text='Как открыть счёт, подскажите, пожалуйста!!!'
r=balabolka_tts(text)
print(r)