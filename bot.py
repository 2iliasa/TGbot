import telebot 
from telebot import types
import psycopg2
from dotenv import dotenv_values
import datetime
import numpy as np
config = dotenv_values()
bot = telebot.TeleBot(config['TOKEN'])

def reg_check(message):         # Функция проверки регистрации. Обращаается к бд и смотрит есть ли в базе регистраций запись id и активна ли она
    try:
        connection = psycopg2.connect(
            host = config['HOST'],
            user = config['USER'],
            password = config['PASS'],
            database = config['DB_NAME']
            )
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(
            f"""select reg from users
            where telegramid = {message.chat.id}"""
                )
        reg = bool(cursor.fetchall())
        if reg == True:
            return True 
        else: 
            bot.send_message(message.chat.id,text='Не зарегистрирован')
            return False
    except Exception as _ex:
        print('[REG_CHECK-INFO] Error while working with PostgreSQL',_ex)
    finally:
        if connection:
            connection.close()
            print(f'[REG_CHECK-INFO] PostgreSQL connection closed with value {reg}')

@bot.message_handler(commands=['start'],func=reg_check)                         #начальная команда для вывода кнопок
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton('записать вес')
    markup.add(button)
    bot.send_message(message.chat.id,text='Добро пожаловать', reply_markup=markup)
        
@bot.message_handler(commands=["weight"],func=reg_check)                  #вызов команды для записи веса
def save_weight(message):
        a = bot.send_message(message.chat.id, 'Введите вес:')
        bot.register_next_step_handler(a, save_weight2)               #метод для передачи значения в следующую функцию

@bot.message_handler(commands=['0'])
def save_weight2(message):                                       #запись веса в бд и вызов сообщения об успешной записи
    weight_value = message.text
    date = datetime.date.today()
    save_date = str(datetime.date.today())
    telegramid = message.chat.id
    try: 
        connection = psycopg2.connect(
            host = config['HOST'],
            user = config['USER'],
            password = config['PASS'],
            database = config['DB_NAME']
            )
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(
            f"""INSERT INTO weight(telegramid, weight, date) VALUES
            ({telegramid},{weight_value},('{save_date}'))"""
            )
    except Exception as _ex:
        print('[INFO] Error while working with PostgreSQL',_ex)
    finally:
        if connection:
            connection.close()
            print('[INFO] PostgreSQL connection closed')
    bot.send_message(message.chat.id, f'Записано: {date} {message.text}')

@bot.message_handler(commands=["замеры"],func=reg_check)                 
def save_measurment(message):
    a = bot.send_message(message.chat.id, f"Введите замеры в формате:'A,B,C..', в порядке грудь, левая рука, правая рука, талия, жопа, левое бедро, правое бедро")
    bot.register_next_step_handler(a,save_measurment2)

@bot.message_handler(commands=['0'])
def save_measurment2(message):                                       
    measurment = message.text
    measurment = measurment.split(',')
    measurment = np.array(measurment,dtype=int)
    save_date = str(datetime.date.today())
    telegramid = message.chat.id
    try: 
        connection = psycopg2.connect(
            host = config['HOST'],
            user = config['USER'],
            password = config['PASS'],
            database = config['DB_NAME']
            )
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(
            f"""INSERT INTO measurments(telegramid,chest, left_arm, right_arm, waist, butt, left_hip, right_hip,date) VALUES
            ({telegramid},{measurment[0]},{measurment[1]},{measurment[2]},{measurment[3]},{measurment[4]},{measurment[5]},{measurment[6]},('{save_date}'))"""
            )
    except Exception as _ex:
        print('[INFO] Error while working with PostgreSQL',_ex)
    finally:
        if connection:
            connection.close()
            print('[INFO] PostgreSQL connection closed')
    telegramid = message.chat.id

bot.infinity_polling()