import telebot
import config
import time
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
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row('Partner')
        markup.row('Consultant')
        bot.send_message(message.chat.id, "Got it! Now tell us who you are.", reply_markup=markup)
        # bot.send_message(message.chat.id,"Got it! Now you shall choose your group")
def update_stage(message, stage):
    query = """UPDATE public."user"
                SET stage={}
                WHERE id={};"""
    query_result = db_query.execute_query(query.format(stage, message.chat.id), is_dml=True)
    # if query_result.success:
        # bot.send_message(message.chat.id,"Got it! Now we are ready to help you!\nPress /menu to start")

@bot.message_handler(commands=['start'])
def insert_into_a_db(message):
    # print('a')
    query = """SELECT auth
	        FROM public."user"
            WHERE id={};"""
    query_result=db_query.execute_query(query.format(message.chat.id))
    if len(query_result.value)<1:
        query ="""INSERT INTO public."user"
        (id, full_name_telegram,stage,auth)
        VALUES ({},'{}',{}, False);"""
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
        #     markup = telebot.types.ReplyKeyboardMarkup()
        #     markup.row('Group A')
        #     markup.row('Group B')
        #     bot.send_message(message.chat.id, "Сhoose your group!", reply_markup=markup)
    pass

@bot.message_handler(regexp=config.secret_key)
def login(message):
    # print('a')
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

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data:
            query = """SELECT full_name_provided
                          	        FROM public."user"
                                      WHERE id={};"""
            query_result = db_query.execute_query(query.format(call.message.chat.id))
            if call.message.chat.username:
                bot.send_message(call.data, query_result.value[0][0]+' (@'+call.message.chat.username+') will come with you!')
            else:
                bot.send_message(call.data, query_result.value[0][0] + ' will come with you!')
            query = """SELECT full_name_provided
                                      	        FROM public."user"
                                                  WHERE id={};"""
            query_result = db_query.execute_query(query.format(call.data))
            bot.answer_callback_query(call.id, text="Done!")
            bot.send_message(call.message.chat.id, 'Invitation from ' + query_result.value[0][0] + ' accepted.')
    pass
            # bot.send_message(call.data, call.message.chat.username'test')
            # for data in call.message.entities[1]:
            #     print((data))


@bot.message_handler(func=lambda message: login_check(message))
def dialog(message):
    stage = stage_check(message)
    # if stage==3:

    # User name asked
    if stage==1:
        update_name(message)
#     # Office name asked
#     if stage==3:
#         query = """SELECT id
#             	        FROM public."user"
#                         WHERE stage=4;"""
#         query_result = db_query.execute_query(query.format(message.chat.id))
#         for id in query_result:
#
#             bot.send_message(id, """Now you can take an offer to dine with partners""", reply_markup=markup)
    pass

@bot.message_handler(content_types='text')
def default_answer(message):
    bot.send_message(message.chat.id, "You are not authorized")
    pass

while True:
    # bot.polling(none_stop=True)
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(e)
        time.sleep(15)