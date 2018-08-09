import re
from pymorphy2 import analyzer as an
import nltk
import requests
import time
import flask
from flask import request, Flask
import json
import pandas as pd
import os

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

########################################################################################################################
########################################################################################################################
#                                        1 GRAPH PART

s0 = """Здравствуйте! Я электронный консультант по подбору персонала компании ММК. Я помогу Вам подобрать вакансию в нашей компании. Пожалуйста, обратите внимание, что, продолжая, вы принимаете наше соглашение об обработке персональных данных. Продолжить? Введите 'даа' для продолжения,'нет' для выхода."""
s1 = "Напишите, пожалуйста, Ваше имя и фамилию. Пример: 'Иван Иванов'. Для выхода введите 'нет', для возвращения назад введите 'назад'."
s2 ="рад познакомиться. Напишите, пожалуйста, свой номер телефона в формате… Пример: '8 92 77 04 38 07'. Для выхода введите 'нет', для возвращения назад введите 'назад'."
s3 = """выберите, пожалуйста, интересующую Вас профессию. Для выхода введите 'нет', для возвращения назад введите 'назад'."""
s4 = '''подождите минуту, я ищу вакансии по указанной вами профессии. Извините, я не смог найти вакансии по Вашему запросу. Вы можете поменять данные и попробовать еще раз. Для повторного поиска введите 'даа' или 'назад', для  выхода введите 'нет'.'''
s5 = '''подождите минуту, я ищу вакансии по указанной вами профессии. По Вашему запросу есть вакансия: '''
s6 = '''заполните, пожалуйста резюме. На Ваш телефон сейчас придет СМС с паролем для открытия опросника.Заполнить? Введите 'даа' для продолжения,'нет' для выхода,'назад' для возвращения назад.'''
F = '''спасибо за Ваше резюме! Введите 'назад' для возвращения назад, либо  введите любую фразу для завершения.'''
E = '''До свидания!'''

d3={0:s0,1:s1,2:s2,3:s3,4:s4,5:s5,6:s6,7:F,8:E}

graph_weights3 = {0: [1,1,0,0,0,0,0,0,1],
         1: [1,1,1,0,0,0,0,0,1],
         2: [0,1,1,1,0,0,0,0,1],
         3: [0,0,1,0,1,1,0,0,1],
         4:[0,0,0,1,1,0,0,0,1],
         5:[0,0,0,1,0,1,1,0,1],
         6:[0,0,0,0,0,1,1,1,1],
         7:[0,0,0,0,0,0,1,0,1],
         8:[0,0,0,0,0,0,0,0,0]}


graph3 = {0: [0,1,8],
         1: [0,1,2,8],
         2: [1,2,3,8],
         3: [2,4,5,8],
         4:[3,4,8],5:[3,5,6,8],6:[5,6,7,8],7:[6,8],8:[None]}

########################################################################################################################
########################################################################################################################
#                                          2 BOT PART


path_to_fs_mmk=os.getcwd() # прописываем пути к файлам
path_to_resources=os.path.join(path_to_fs_mmk,'resources')

data=['prename','name','phone','resume'] # список для сохранения данных пользователя
profession_data=['profession','profession_info']  # список для сохранения данных об искомой вакансии и результатах поиска


good_words=set(['да','хорошо','давайте'])
bad_words=set(['нет','пока'])
back_words=set(['назад','вернуться','back'])

filename_vacancies=os.path.join(path_to_resources,'Vacancies_list.xlsx')
filename_people=os.path.join(path_to_resources,'People_list.xlsx')

df=pd.read_excel(filename_people,encoding='1251')

def preprocess_message(message): # препроцессинг сообщения
    # здесь будет препроцессинг сообщения
    return message.lower()



def save_to_xlsx(data, path): # для сохранения даннных в эксель
    writer = pd.ExcelWriter(path, engine='openpyxl')
    wb  = writer.book
    data.to_excel(writer,'Лист1', index=False)
    wb.save(path)

def save_data(data,df):
    # здесь будем сохранять полученные от пользователя данные в эксель файл
    for i in range(0,len(data)):
        data[i]=data[i].title() # фамилия-имя с большой буквы
    df.loc[df.shape[0]]=data
    save_to_xlsx(df,filename_people)


def make_list_vacancies_from_excel(filename):
    ds=pd.read_excel(filename)
    x=ds.values.tolist()
    list_vacancies_info=x
    return list_vacancies_info

list_vacancies_info=make_list_vacancies_from_excel(filename_vacancies) #получаем список открытых вакансий из файла

def search(profession,list_vacancies_info): # функция поиска вакансии
    answer_list=[]
    for i in range(0,len(list_vacancies_info)):
        a=re.search(profession.lower(), list_vacancies_info[i][0])
        b=re.search(profession.title(), list_vacancies_info[i][0])
        if ((a is not None) | (b is not None)):
            answer_list.append(list_vacancies_info[i])
    s=''
    for i in range(0,len(answer_list)):
        s=s+' профессия: '+str(answer_list[i][0])+'; цех: '+str(answer_list[i][1])+'; требования: '+str(answer_list[i][2])+'; режим работы: '+str(answer_list[i][3])
        s=s+' \n'
    return s

def search_answer(profession,list_vacancies_info): # функция для получения списка ответов на запрос
    answer_list=[]
    for i in range(0,len(list_vacancies_info)):
        a=re.search(profession.lower(), list_vacancies_info[i][0])
        b=re.search(profession.title(), list_vacancies_info[i][0])
        if ((a is not None) | (b is not None)):
            answer_list.append(list_vacancies_info[i])
    return answer_list

def extended_search(profession,list_vacancies_info): # черновик, пока не работает
    answer_list=[]
    #answer_list0=search_answer(profession,list_vacancies_info) # получаем результаты для точного поиска по введённой фразе пользователем
    profession_list=profession.split() # получаем список
    for j in range(0,len(profession_list)): # ищем по всем словам  запроса
        for i in range(0,len(list_vacancies_info)):
            a=re.search(profession_list[j].lower(), list_vacancies_info[i][0])
            b=re.search(profession_list[j].title(), list_vacancies_info[i][0])
            if ((a is not None) | (b is not None)):
                answer_list.append(list_vacancies_info[i])
    #answer_list = list(set(answer_list) - set(answer_list0)) # убираем результаты точного запроса из результатов расширенного запроса(чтобы не было повторений)
    #answer_list=answer_list0+answer_list  # добавляем в начало результаты точного запроса в результаты расширенного запроса(чтобы не было повторений)
    answer_list=set(answer_list)
    s=''
    for i in range(0,len(answer_list)):
        s=s+' профессия: '+str(answer_list[i][0])+'; цех: '+str(answer_list[i][1])+'; требования: '+str(answer_list[i][2])+'; режим работы: '+str(answer_list[i][3])
        s=s+' \n'
    return s



analyzer = an.MorphAnalyzer()

namesType1 = {'Name'}

def test_name_only(word):  # используется для выделения имени
    return len(analyzer.parse(word)[0].tag.grammemes & namesType1) > 0


def extract_name(a):  # выделение имени
    string = a
    res = []
    for word in nltk.tokenize.word_tokenize(str(string), language='russian'):
        # word = word.replace(',', '')
         if test_name_only(word):
                word=analyzer.parse(word)[0].normal_form #
                word=word.title()
                res.append(word)
    return ' '.join(res)

def get_message_mmk(s):
    # здесь будем получать сообщение клиента
    #print(s)
    return s

def get_name(s):
    #здесь будем получать имя клиента
    name=extract_name(s)
    if (name==''):
        name='Уважаемый пользователь'
    return name

def get_profession(s):
    #здесь будем извлекать профессию с помощью Томиты (aka извлечение фактов)
    #или набора правил после препроцессинга (опять же с Томитой)
    return s

def get_profession_set(filename):
    #здесь будем получать список вакансий
    profession_set=set(['машинист', 'загрузчик', 'вальцовщик'])
    return profession_set

def get_profession_info(profession):
    #здесь будем получать информацию(профессия,цех,требования,рехим работы) и выводить в строчку
    s=profession_data[1]
    return s

def get_name_from_context(context): # убрать контекст потом
    #здесь будем получать имя из ранее сохранённого контекста
    name=data[0]
    name=name.title()
    if (name==''):
        name='Уважаемый пользователь'
    return name

def get_phone_from_context():
    #здесь будем получать телефон из ранее сохранённого контекста
    return '8800555555'

def get_profession_from_context():
    # здесь будем получать профессию из ранее сохранённого контекста
    return profession_data[0]

def get_resume_from_context():
    #здесь будем получать резюме из ранее сохранённого контекста
    return 'resume.txt'

def get_name_prename(name):
    name_prename=name.split()
    only_name=name_prename[0]
    prename=''
    if (len(name_prename)>=2): # костыль
        prename=name_prename[1]
    return only_name,prename


def paste_name(s,name):
    #здесь будем вставлять имя клиента в реплику
    # планируется вставлять вместо 'Иван'
    return name+ ', '+s

def paste_profession_info(replic,profession_info):
    #здесь будем вставлять информацию (профессия,цех,требования,рехим работы) о профессии в соответствующую реплику
    return replic+' '+profession_info


def check_phone(phone):
    # здесь будет проверка введённого телефона на корректность данных


    if (len(phone)!=11):
        return False
    if (phone!= ' '.join(re.findall("[0-9]+", phone)) ):
        return False
    return True

def check_name(name):
    # здесь будет проверка введённого ФИ на корректность данных

    if (len(name.split())!=2):
        return False
    if (name!= ' '.join(re.findall("[а-яА-я]+", name)) ):
        return False
    if ((name.split()[0].title()!=name.split()[0])|(name.split()[1].title()!=name.split()[1])):
        return False
    return True

def check_resume(resume):
    # здесь будет проверка прикреплённого резюме на корректность
    return True

def check_profession(profession):
    # здесь будет проверка введённой(искомой) вакансии на корректность данных
    return True

def correct_message(mode):
    if (mode == 'phone'):
        return """Пожалуйста, убедитесь в правильности введённого номера телефона! 
        Нужно ввести ТОЛЬКО телефон в формате ... Пример: 89277043807"""
    if (mode == 'name'):
        return "Пожалуйста, убедитесь в правильности введённых данных! Нужно ввести ТОЛЬКО имя и фамилию. Пример: Иван Иванов"
    if (mode == 'resume'):
        return "Пожалуйста, прикрепите резюме в форматах .doc, .docx!"
    if (mode == 'profession'):
        return "Пожалуйста, убедитесь в правильности введённой вакансии! Нужно ввести ТОЛЬКО вакансию. Пример: загрузчик"
    return "Пожалуйста, убедитесь в правильности введённых данных!"


reg = re.compile(r'[^0-9]')

def predict_state_mmk(mess,state,context):
    replic='Начальная'
    one_state=True# переменная-флаг, для того,чтобы делать только один переход из одного состояния в другое
    message=get_message_mmk(mess)# получаем сообщение от пользователя
    if ((state==0) & one_state):# из нулевого состояния можем перейти в состояния 1,8(E)
        one_state=False
        if (message in good_words): #переход из нулевого состояния в состояние 1
            state=1
            replic=d3[state]
        elif (message in bad_words): #переход из нулевого состояния в состояние 8(E)
            state=8
            replic=d3[state]
        else: #переход из нулевого состояния в состояние 0
            state=0
            replic=d3[state]
    if ((state==1) & one_state): #из первого состояния можем перейти в состояния 0,1,2,8(E)
        one_state=False
        if (message in back_words): #переход из первого состояния в состояние 0
            state=0
            replic=d3[state]
        elif (message in bad_words): #переход из первого состояния в состояние 8
            state=8
            replic=d3[state]
        else:
            if not check_name(message) :#  здесь будет проверка имени и петля графа
                return correct_message('name'),state
        #name = get_name(message)  # получаем имя пользователя
            data[0],data[1] = get_name_prename(message)# получаем имя и фамилию пользователя
            state = 2 # переход из первого состояния в состояние 2
            replic=paste_name(d3[state],data[0])# вставляем в сообщение имя пользователя

    if ((state==2) & one_state): #из второго состояния можем перейти в состояния 1,2,3,8(E)
        one_state=False
        if (message in back_words):  # переход из второго состояния в состояние 1
            state = 1
            replic = d3[state]
        elif (message in bad_words):  # переход из второго состояния в состояние 8(E)
            state = 8
            replic = d3[state]
        else:
            message = reg.sub('', message)
            if not check_phone(message) :#  здесь будет проверка телефона и петля графа
                return correct_message('phone'),state
            data[2] = message # получаем телефон пользователя
            #переход из второго состояния в состояние 3
            state=3
            name=get_name_from_context(context);# получаем имя пользователя из контекста
            replic=paste_name(d3[state],name)# вставляем в сообщение имя пользователя
    if ((state==3) & one_state): # из третьего состояния можем перейти в состояния 2,4,5,8(E)
        one_state=False
        profession_data[0]=get_profession(message) #получаем вакансию, интересную для пользователя
        profession_data[1]=search(profession_data[0],list_vacancies_info) # поиск вакансий#search
        if (profession_data[1]!=''): #переход из третьего состояния в состояние 5
            state=5
            replic=paste_profession_info(d3[state],profession_data[1])#вставляем информацию о вакансии в сообщение
            name=get_name_from_context(context) # получаем имя пользователя из контекста
            replic=paste_name(replic,name)+'''Откликнуться? Введите 'даа' для продолжения,'нет' для выхода,'назад' для возвращения назад.''' # вставляем имя пользователя в сообщение
        else:  #переход из третьего состояния в состояние 4
            state=4
            name=get_name_from_context(context) # получаем имя пользователя из контекста
            replic=paste_name(d3[state],name) # вставляем имя пользователя в сообщение
        if (message in back_words):
            state=2
            name=get_name_from_context(context)# получаем имя пользователя
            replic=paste_name(d3[state],name)# вставляем в сообщение имя пользователя
        if (message in bad_words): #переход из третьего состояния в состояние 8(E)
            state=8
            replic=d3[state]
    if ((state==4) & one_state): # из четвёртого состояния можем перейти в состояния 3,8(E)
        one_state=False
        if ((message in good_words)|(message in back_words)):# переход из четвёртого состояния в состояние 3
            state=3
            name=get_name_from_context(context);# получаем имя пользователя из контекста
            replic=paste_name(d3[state],name)# вставляем в сообщение имя пользователя
        elif (message in bad_words):  # переход из четвёртого состояния в состояние 8(E)
            state=8
            replic=d3[state]
        else: #переход из четвёртого состояния в состояние 4
            state = 4
            name = get_name_from_context(context)  # получаем имя пользователя из контекста
            replic = paste_name(d3[state], name)  # вставляем имя пользователя в сообщение
    if ((state==5) & one_state): # из пятого состояния можем перейти в состояния 3,6,8(E)
        one_state=False
        if (message in good_words):#переход из пятого состояния в состояние 6
            state=6
            name = get_name_from_context(context);  # получаем имя пользователя из контекста
            replic = paste_name(d3[state], name)  # вставляем в сообщение имя пользователя
        elif (message in back_words): # переход из пятого состояния в состояние 3
            state=3
            name=get_name_from_context(context);# получаем имя пользователя из контекста
            replic=paste_name(d3[state],name)# вставляем в сообщение имя пользователя
        elif (message in bad_words): #переход из пятого состояния в состояние 8(E)
            state=8
            replic=d3[state]
        else:
            state=5 # здесь будет переход в пятое состояние
            replic = paste_profession_info(d3[state], profession_data[1])  # вставляем информацию о вакансии в сообщение
            name = get_name_from_context(context)  # получаем имя пользователя из контекста
            replic = paste_name(replic, name) + '''Откликнуться? Введите 'даа' для продолжения,'нет' для выхода,'назад' для возвращения назад.'''   # вставляем имя пользователя в сообщение
    if ((state==6) & one_state): # из шестого состояния можем перейти в состояния 5,6,7(F),8(E)
        one_state=False
        if not check_resume(message) :#  здесь будет проверка резюме и петля графа
                return correct_message('resume'),state
        data[3] = 'True resume'  # здесь будем получать(?) резюме пользователя
        if (message in good_words): #переход из шестого состояния в состояние 7(F)
            state=7
            replic=d3[state]
            name = get_name_from_context(context)  # получаем имя пользователя из контекста
            replic = paste_name(replic, name) # вставляем имя пользователя в сообщение
        elif (message in back_words):#переход из шестого состояния в состояние 5
            state=5
            #profession_data[0]=get_profession_from_context() #получаем професссию из ранее сохранённого контекста
            #profession_info=search(profession_data[0],list_vacancies_info) # поиск вакансий
            replic=paste_profession_info(d3[state],profession_data[1])#вставляем информацию о вакансии в сообщение
            name=get_name_from_context(context) # получаем имя пользователя из контекста
            replic=paste_name(replic,name)+''' Откликнуться? Введите 'даа' для продолжения,'нет' для выхода,'назад' для возвращения назад.''' # вставляем имя пользователя в сообщение
        elif (message in bad_words): #переход из шестого состояния в состояние 8(E)
            state = 8
            replic = d3[state]
        else: #переход из шестого состояния в состояние 6
            state=6
            name = get_name_from_context(context);  # получаем имя пользователя из контекста
            replic = paste_name(d3[state], name)  # вставляем в сообщение имя пользователя

    if ((state==7) & one_state): # из седьмого состояния можем перейти в состояния 6,8(E)
        one_state=False
        state=8 #переход из седьмого состояния в состояние 8(E)
        replic=d3[state]
        if (message in back_words):#переход из седьмого состояния в состояние 6
                state=6
                replic=d3[state]
                name = get_name_from_context(context)  # получаем имя пользователя из контекста
                replic = paste_name(replic, name)  # вставляем имя пользователя в сообщение
        if (state==8):
            state=0
            save_data(data,df)
            replic=d3[state]
    print(state)
    print(replic)
    if replic=='Начальная':
        state=0
        replic=d3[state]
    return replic,state

########################################################################################################################
########################################################################################################################
#                                                       3 VK PART

def write_msg(user_id, message): # написать сообщение
    # vk.method('messages.send', {'user_id':user_id,'message':s})
    request = 'https://api.vk.com/method/messages.send?&user_id=' + str(
        user_id) + '&message=' + message + '&v=5.73&access_token=850ab7921c191bc274f2c3d2010a30f4f99c537a4b6bdb3ad661280b1035c76183042d917855b55c55bb5'
    r = requests.post(request, verify=False)


def read_msg(): # прочитать сообщение
    values = {'out': 0, 'count': 10, 'time_offset': 60}
    # vk.method('messages.get', values)
    request = requests.get(
        'https://api.vk.com/method/messages.get?values=values&v=5.73&access_token=850ab7921c191bc274f2c3d2010a30f4f99c537a4b6bdb3ad661280b1035c76183042d917855b55c55bb5',
        verify=False)
    x = request.json();
    count = x['response']['count']
    message = x['response']['items'][0]['body']
    user_id = x['response']['items'][0]['user_id']
    return count, user_id, message


def send_message(user_id, message): # отправить сообщение
    write_msg(user_id, message)


def get_message(): # получить сообщение
    count, user_id, message = read_msg()
    return count, message


def vk_get_mess(count,count_prev): # получить сообщение вконтакте
    while(count<=count_prev):
        count,s=get_message()
        #print('count='+str(count)+' count_prev='+str(count_prev))
        #time.sleep(3)
    count_prev=count
    return s,count_prev,count

def mmk_bot_vk(graph, graph_weights, count_prev):  # сценарный бот ммк (один раз выполнится) вк
        user_id = 484230842#28499999#'stepanov__s'#
        count = count_prev
        mess1 = s0
        send_message(user_id, mess1)
        s, count_prev, count = vk_get_mess(count, count_prev)
        # s=preprocess_all(s)
        #w = graph_weights[0]
        replic, state = predict_state_mmk(s, 0, '')
        send_message(user_id, replic)
        context = s
        while (graph[state][0] != None):
            s, count_prev, count = vk_get_mess(count, count_prev)
            # s=preprocess_all(s)
            replic, state = predict_state_mmk(s, state, context)  # context
            send_message(user_id, replic)
            context = context + ' ' + s


def vk_main_mmk_bot( graph, graph_weights):  # сценарный бот ммк(зациклен) вк
    while True:
        request = requests.get(
            'https://api.vk.com/method/messages.get?values=values&v=5.73&access_token=850ab7921c191bc274f2c3d2010a30f4f99c537a4b6bdb3ad661280b1035c76183042d917855b55c55bb5',
            verify=False)
        x = request.json()
        count_prev = x['response']['count']
        mmk_bot_vk(graph, graph_weights, count_prev)
        #time.sleep(1)

def get_user_id(): #здесь будем получать id пользователя, с которым будем вести диалог
    # это будет первый пользователь, кто напишет боту, после включения бота
    count,user_id,message=read_msg()

    pass

########################################################################################################################
########################################################################################################################
#                                                   4  FLASK PART




def predict_state_mmk_flask(message,state,context):
    answer,state=predict_state_mmk(message,state,context)
    context=context+ ' '+ message
    return answer,context,state

def get_context(context=None):
    if (context==None):
        context=''
    return context

def get_state(state=None):
    if (state==None):
        state=0
    return int(state)



#app=Flask(__name__)


#@app.route("/getAnswer_mmk",methods = ['GET','POST'])# getAnswer_mmk
#def getAnswer_mmk():
    # message=request.args['message']
    # state=get_state(request.args.get('state'))
    # context=get_context(request.args.get('context'))
 #   if request.method == 'GET':
 #       message=request.args['message']
  #      state= get_state(request.args.get('state'))
  #      context= get_context(request.args.get('context'))
   # if request.method == 'POST':
   #     print(request.data)
   #     data = json.loads(request.data.decode('utf-8'))
   #     message = data['message']
    #    state = get_state(data.get('state'))
   #     context = get_context(data.get('context'))

    #message=preprocess_all(message)
   # answer,context,state = predict_state_mmk_flask(message,state,context)#state
   # if (graph3[state][0] == None):
    #    leaf=1
   # else:
    #    leaf=0
    #print(answer)
    #return flask.jsonify({'message':answer,'context':context,'state':state,'final_dialog':leaf,'confidence':1}) #'context':context,'state':state


#########################################################################################################################
########################################################################################################################
#                                                       5 MAIN
#vk_main_mmk_bot(graph3,graph_weights3)
#app.run(host='0.0.0.0',debug=True,port=9091)
#app.run()
