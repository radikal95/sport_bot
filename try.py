#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.
import time

import logging
import telebot

API_TOKEN = '622726947:AAHOVDDfxJDbxyMNFBYx72OZfHPPG8AvnUY'

bot = telebot.TeleBot(API_TOKEN)

logging.basicConfig(filename="sample.log", level=logging.INFO)
# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)


while True:
    # bot.polling(none_stop=True)
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(e)
        time.sleep(15)