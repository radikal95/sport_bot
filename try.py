import telebot
import config
import time
import datetime
import logging
import json
import zipfile
import os
from openpyxl import Workbook
bot = telebot.TeleBot(config.token)
logging.basicConfig(filename="sample.log", level=logging.INFO)

@bot.message_handler(content_types='text')
def default_answer(message):
    bot.send_message(message.chat.id, message.text)
    pass

while True:
    # bot.polling(none_stop=True)
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(e)
        time.sleep(15)