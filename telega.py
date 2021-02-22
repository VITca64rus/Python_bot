import telebot
from collections import defaultdict
from telebot import types
import sqlite3

def ensure_connection(func):
    def inner(*args,**kwargs):
        with sqlite3.connect('restorans.db') as conn:
            return func(*args,conn=conn,**kwargs)
    return inner


@ensure_connection
def init_db(conn,force: bool = False):
    c=conn.cursor()

    if force:
        c.execute('DROP TABLE IF EXISTS restorans')

    c.execute('''
        CREATE TABLE IF NOT EXISTS restorans(
            id INTEGER PRIMARY KEY,
            id_user TEXT NOT NULL,
            title TEXT NOT NULL,
            photo TEXT NOT NULL,
            lat TEXT NOT NULL,
            lon TEXT NOT NULL 
        )
    ''')
    conn.commit()

@ensure_connection
def add_bd(conn,id,title,photo,lat,lon):
    c = conn.cursor()
    c.execute('INSERT INTO restorans (id_user, title, photo, lat, lon) VALUES(?, ?, ?, ?, ?)',
              (id,title,photo,lat,lon)
              )
    conn.commit()


bot = telebot.TeleBot('1673810332:AAHAufEOkmeDzbbv5Roo0h9tt38W9C7I8ng')
START, ADD, PHOTO, LOCATION, CONFIRMATION = range(5)
USER_STATE=defaultdict(lambda:START)
RESTORANS=defaultdict(lambda :{})

def get_state(message):
    return USER_STATE[message.chat.id]
def update_state(message,state):
    USER_STATE[message.chat.id]=state

def update_restorans(user_id,key,value):
    RESTORANS[user_id][key]=value
def get_restorans(user_id):
    return RESTORANS[user_id]

def create_keyboard():
    buttons = []
    keyboard=types.InlineKeyboardMarkup(row_width=2)
    buttons.append(types.InlineKeyboardButton(text='Да',callback_data='yes_save'))
    buttons.append(types.InlineKeyboardButton(text='Нет', callback_data='no_save'))
    keyboard.add(*buttons)
    return keyboard

@bot.message_handler(commands=['add'])
def get_add(message):
    bot.send_message(chat_id=message.chat.id,text='Введите название ресторана')
    update_state(message, ADD)

@bot.message_handler(func=lambda message: get_state(message) == ADD)
def get_title(message):
    #Название
    update_restorans(message.chat.id,'title',message.text)
    bot.send_message(chat_id=message.chat.id,text='Прикрепите фото')
    update_state(message, PHOTO)

@bot.message_handler(content_types=['photo'])
def get_photo(message):
    if get_state(message)==PHOTO:
        photo_id = message.photo[0].file_id
        #bot.send_photo(message.chat.id, idphoto )
        update_restorans(message.chat.id,'photo',photo_id)
        bot.send_message(chat_id=message.chat.id,text='Прикрепите геометку')
        update_state(message, LOCATION)

@bot.message_handler(content_types=['location'])
def get_location(message):
    if get_state(message) == LOCATION:
        update_restorans(message.chat.id,'location',message.location)
        keyboard=create_keyboard()
        bot.send_photo(message.chat.id, RESTORANS[message.chat.id]['photo'],
                       caption='Хочешь сохранить ресторан "{}" по координатам {},{}?'.format(
                           RESTORANS[message.chat.id]['title'],RESTORANS[message.chat.id]['location'].latitude,
                          RESTORANS[message.chat.id]['location'].longitude),reply_markup=keyboard)
        update_state(message, CONFIRMATION)

@bot.callback_query_handler(func=lambda x: True)
def callback_handler(callback_query):
    if callback_query.data=='yes_save' and get_state(callback_query.message)==CONFIRMATION:
        bot.send_message(chat_id=callback_query.message.chat.id , text='Ресторан сохранен')
        add_bd(id=callback_query.message.chat.id,
               title=RESTORANS[callback_query.message.chat.id]['title'],
               photo=RESTORANS[callback_query.message.chat.id]['photo'],
               lat=RESTORANS[callback_query.message.chat.id]['location'].latitude,
               lon=RESTORANS[callback_query.message.chat.id]['location'].longitude
               )
    elif callback_query.data=='no_save' and get_state(callback_query.message)==CONFIRMATION:
        bot.send_message(chat_id=callback_query.message.chat.id, text='Ресторан не сохранен')
    else:
        bot.send_message(chat_id=callback_query.message.chat.id, text='Сохранить несколько раз не возможно')
    update_state(callback_query.message, START)

@ensure_connection
def get_restoran(conn,id):
    c=conn.cursor()
    c.execute('SELECT * FROM restorans WHERE id_user=?',(id,))
    return c.fetchall()

@ensure_connection
def del_restoran(conn,id):
    c=conn.cursor()
    c.execute('DELETE FROM restorans WHERE id_user=?',(id,))
    return c.fetchall()


@bot.message_handler(commands=['list'])
def get_list(message):
    restorans=get_restoran(id=message.chat.id)
    if restorans:
        for restoran in restorans:
            bot.send_photo(message.chat.id,restoran[3],caption='Ресторан "{}", координаты: {},{}'.format(restoran[2],
                                                                    restoran[4],restoran[5]))
    else:
        bot.send_message(message.chat.id,text='Данных нет')
@bot.message_handler(commands=['reset'])
def reset_list(message):
    del_restoran(id=message.chat.id)
    bot.send_message(message.chat.id,text='Данные удалены')


init_db()
bot.polling(none_stop=True, interval=0)


