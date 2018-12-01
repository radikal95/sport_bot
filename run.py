import telebot
import config
import time
import datetime
import logging
import json
from db_tool import DbQuery

db_query = DbQuery()
bot = telebot.TeleBot(config.token)
logging.basicConfig(filename="sample.log", level=logging.INFO)

def stage_check(message):
    query = """SELECT stage
        	        FROM public."user"
                    WHERE id={};"""
    query_result = db_query.execute_query(query.format(message.chat.id))
    if len(query_result.value) < 1:
        return None
    else:
        return query_result.value[0][0]

def login_check(message):
    query = """SELECT auth
    	        FROM public."user"
                WHERE id={};"""
    query_result = db_query.execute_query(query.format(message.chat.id))
    if len(query_result.value)<1:
        return False
    else:
        return query_result.value[0][0]

def update_name(message):
    query = """UPDATE public."user"
            SET full_name_provided ='{}', stage=2
            WHERE id={};"""
    query_result =  db_query.execute_query(query.format(message.text, message.chat.id), is_dml=True)
    if query_result.success:
        bot.send_message(message.chat.id, "Got it! Send any text to confirm that you have exercised today")
        # bot.send_message(message.chat.id,"Got it! Now you shall choose your group")

def update_stage(message, stage):
    query = """UPDATE public."user"
                SET stage={}
                WHERE id={};"""
    query_result = db_query.execute_query(query.format(stage, message.chat.id), is_dml=True)

def update_exercise(message):
    query = """SELECT last_ex_date, exercise
    	        FROM public."user"
                WHERE id={};"""
    query_result = db_query.execute_query(query.format(message.chat.id))
    exercise = int(query_result.value[0][1])
    # last_ex_date = datetime.datetime.strptime(query_result.value[0][0], '%Y-%m-%d')
    if (datetime.date.today().day==query_result.value[0][0].day) and (datetime.date.today().month==query_result.value[0][0].month) and (datetime.date.today().year==query_result.value[0][0].year):
        bot.send_message(message.chat.id, "Sorry, you have already submitted your training today")
    else:
        query = """UPDATE public."user"
                                SET exercise={},last_ex_date='{}'
                                WHERE id={};"""
        query_result = db_query.execute_query(query.format(exercise + 1,datetime.datetime.now(), message.chat.id), is_dml=True)
        bot.send_message(message.chat.id, "Bravo! We assigned 1 point to you!")


@bot.message_handler(regexp='/start')
def insert_into_a_db(message):
    # print('a')
    query = """SELECT auth
	        FROM public."user"
            WHERE id={};"""
    query_result=db_query.execute_query(query.format(message.chat.id))
    if len(query_result.value)<1:
        query ="""INSERT INTO public."user"
        (id, full_name_telegram,stage,auth, exercise, last_ex_date)
        VALUES ({},'{}',{}, False, 0,'2000-01-01');"""
        name = 'Unknown user'
        if message.chat.first_name:
            name = str(message.chat.first_name)
        if message.chat.last_name:
            name = name + ' ' + str(message.chat.last_name)
        query_result=db_query.execute_query(query.format(message.chat.id,name,0),is_dml=True)
        if (query_result.success):
            bot.send_message(message.chat.id, "So, tell us the key")
    else:
        if not query_result.value[0][0]:
            bot.send_message(message.chat.id, "Tell us the key")
        else:
            bot.send_message(message.chat.id, "You are already logged in")
    pass

@bot.message_handler(regexp=config.secret_key)
def login(message):
    query = """SELECT auth
    	        FROM public."user"
                WHERE id={};"""
    query_result = db_query.execute_query(query.format(message.chat.id))
    if len(query_result.value)<1:
        bot.send_message(message.chat.id, "You are not authorized")
    else:
        if not query_result.value[0][0]:
            query = """UPDATE public."user"
                    SET auth = true, stage=1
                    WHERE id={};"""
            query_result=db_query.execute_query(query.format(message.chat.id),is_dml=True)
            # print(query_result)
            if query_result.success:
                bot.send_message(message.chat.id, "<b>The password is correct!</b> \n"
                "Please, answer one simple question. \nWhat is your full name?""", parse_mode='HTML')
    pass


# @bot.callback_query_handler(func=lambda call: True)
# def callback_inline(call):
#     if call.message:
#         if call.data:
#             query = """SELECT full_name_provided
#                           	        FROM public."user"
#                                       WHERE id={};"""
#             query_result = db_query.execute_query(query.format(call.message.chat.id))
#             if call.message.chat.username:
#                 bot.send_message(call.data, query_result.value[0][0]+' (@'+call.message.chat.username+') will come with you!')
#             else:
#                 bot.send_message(call.data, query_result.value[0][0] + ' will come with you!')
#             query = """SELECT full_name_provided
#                                       	        FROM public."user"
#                                                   WHERE id={};"""
#             query_result = db_query.execute_query(query.format(call.data))
#             bot.answer_callback_query(call.id, text="Done!")
#             bot.send_message(call.message.chat.id, 'Invitation from ' + query_result.value[0][0] + ' accepted.')
#     pass


@bot.message_handler(func=lambda message: login_check(message))
def dialog(message):
    stage = stage_check(message)
    if stage==1:
        update_name(message)
    if stage==2:
        update_exercise(message)
    pass

@bot.message_handler(content_types='text')
def default_answer(message):
    bot.send_message(message.chat.id, "You have not told us the key")
    pass

while True:
    # bot.polling(none_stop=True)
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(e)
        time.sleep(15)