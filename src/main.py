import json
import re

import telebot
from telebot import types


token = open('src/token.txt', 'r').read()
bot = telebot.TeleBot(token)


def find_pkmn(message):
    pkmn = re.sub('/data ', '', message.text)
    pkmn = re.sub('♀', '-f', pkmn)  # For Nidoran♀
    pkmn = re.sub('♂', '-m', pkmn)  # For Nidoran♂
    pkmn = re.sub('[èé]', 'e', pkmn)  # For Flabébé
    pkmn = re.sub(' ', '-', pkmn)
    pkmn = re.sub('[^A-Za-z-]', '', pkmn)
    return pkmn


@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    bot.send_message(cid, 'Hello Trainer!')


@bot.message_handler(commands=['data'])
def pkmn_search(message):
    cid = message.chat.id
    pkmn = find_pkmn(message)
    path = 'dist/gen{}/gen{}.json'

    for i in range(1, 9):
        with open(path.format(i, i), 'r') as f:
            data = json.load(f)
        if pkmn in data:
            pkmn_data = data[pkmn]
            break
    else:
        bot.send_message(cid, 'Pokémon not found :(')
        return None

    bot.send_message(cid, pkmn_data['national'])


bot.polling(none_stop=True)
