import json
import re

import telebot
from telebot import types


token = open('src/token.txt', 'r').read()
bot = telebot.TeleBot(token)


def find_name(message):
    pkmn = re.sub('/data ', '', message.text)
    pkmn = re.sub('♀', '-f', pkmn)  # For Nidoran♀
    pkmn = re.sub('♂', '-m', pkmn)  # For Nidoran♂
    pkmn = re.sub('[èé]', 'e', pkmn)  # For Flabébé
    pkmn = re.sub(' ', '-', pkmn)
    pkmn = re.sub('[^A-Za-z-]', '', pkmn)
    return pkmn


def set_message(pkmn_data):
    base = '''National: {}
Species: {}
Catch Rate: {}
Base Friendship: {}
Growth Rate: {}
Egg Cycles: {}
Artwork: {}
'''
    national = pkmn_data['national']
    species = pkmn_data['species']
    catch_rate = pkmn_data['catch_rate']
    base_friendship = pkmn_data['base_friendship']
    growth_rate = pkmn_data['growth_rate']
    egg_cycles = pkmn_data['egg_cycles']
    artwork = pkmn_data['artwork']

    text = base.format(
        national,
        species,
        catch_rate,
        base_friendship,
        growth_rate,
        egg_cycles,
        artwork
    )
    return text


@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    bot.send_message(cid, 'Hello Trainer!')


@bot.message_handler(commands=['data'])
def pkmn_search(message):
    cid = message.chat.id
    pkmn = find_name(message)
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

    text = set_message(pkmn_data)
    bot.send_message(cid, text)


bot.polling(none_stop=True)
