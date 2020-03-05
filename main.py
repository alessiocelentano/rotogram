import telebot
from telebot import types


token = open('token.txt', 'r').read()
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    bot.send_message(cid, 'Hello Trainer!')


bot.polling(none_stop=True)
