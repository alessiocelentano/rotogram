import json
import re

import telebot
from telebot import types


token = open('src/token.txt', 'r').read()
bot = telebot.TeleBot(token)


def find_name(message):
    pkmn = re.sub('/data ', '', message.text.lower())
    pkmn = re.sub('♀', '-f', pkmn)  # For Nidoran♀
    pkmn = re.sub('♂', '-m', pkmn)  # For Nidoran♂
    pkmn = re.sub('[èé]', 'e', pkmn)  # For Flabébé
    pkmn = re.sub(' ', '-', pkmn)
    pkmn = re.sub('[^a-z-]', '', pkmn)
    return pkmn


def manage_forms(pkmn_data, data):
    if 'forms' in pkmn_data:
        for form in pkmn_data['forms'].items():
            value = pkmn_data['forms'][form[0]][data]
            break
    else:
        value = pkmn_data[data]
    return value


def set_message(pkmn_data):
    base_text = '''<b><u>{}</u></b> <a href="{}">{}</a>\n
<b>National</b>: <i>{}</i>
<b>{}</b>: <i>{}</i>
<b>{}</b>: <i>{}</i>\n
<b>Base stats</b>:
<i>{}</i>
'''
    name = pkmn_data['name']

    national = pkmn_data['national']

    artwork = manage_forms(pkmn_data, 'artwork')

    typee = ''
    for i in manage_forms(pkmn_data, 'type').values():
        typee += '/' + i
    typee = typee[1:]
    if '/' in typee:
        typee_str = 'Type'
    else:
        typee_str = 'Types'

    emoji_dict = {
        'Grass': '🌱',
        'Fire': '🔥',
        'Water': '💧',
        'Flying': '🦅',
        'Bug': '🐞',
        'Normal': '🐾',
        'Dragon': '🐲',
        'Ice': '❄️',
        'Ghost': '👻',
        'Fighting': '💪',
        'Fairy': '🌸',
        'Steel': '⚙️',
        'Dark': '🌙',
        'Psychic': '🔮',
        'Electric': '⚡️',
        'Ground': '🌍',
        'Rock': '🗻',
        'Poison': '☠️'
    }
    first_type = re.split('/', typee)[0]
    emoji = emoji_dict[first_type]

    ability = ''
    for i, j in manage_forms(pkmn_data, 'abilities').items():
        if i == 'hidden_ability':
            ability += '\n' + '<b>Hidden Ability</b>: ' + j
        else:
            ability += '/' + j
    ability = ability[1:]
    if '/' in ability:
        ab_str = 'Abilities'
    else:
        ab_str = 'Ability'

    base_stats = ''
    stats = ['HP', 'Atk', 'Def', 'SpA', 'SpD', 'Spe']
    for base, minn, maxx, stat in zip(
        manage_forms(pkmn_data, 'base_stats').values(),
        manage_forms(pkmn_data, 'min_stats').values(),
        manage_forms(pkmn_data, 'max_stats').values(),
        stats
    ):
        base_stats += stat + ': ' + base + ' (' + minn + '-' + maxx + ')\n'

    text = base_text.format(
        name,
        artwork,
        emoji,
        national,
        typee_str,
        typee,
        ab_str,
        ability,
        base_stats,
    )
    return text


@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    text = '''
⚡️ Zzzt! Ehy. I\'m Rotom! My trainer merged me with a Telegram Bot. \
He\'s teaching me some commanzzz, for now I can tell you basic \
information about all Pokémon using <code>/data</code> command.
'''
    bot.send_message(cid, text, parse_mode='HTML')


@bot.message_handler(commands=['data'])
def pkmn_search(message):
    cid = message.chat.id
    pkmn = find_name(message)

    if message.text == '/data':
        text = '''
⚡️ Zzrrt! My trainer's teaching me many thingzz, \
but I still can't read in thought. Use this syntax: /data + PokémonName
ex.: /data Rotom'
'''
    else:
        with open('dist/pkmn.json', 'r') as f:
            data = json.load(f)
        if pkmn in data:
            text = set_message(data[pkmn])
        else:
            text = '''
Mm-hmm, well, maybe he's an anime character, but he certainly \
izzn't a Pokémon. Zzzt-zzt! ⚡️
'''

    bot.send_message(cid, text, parse_mode='HTML')


bot.polling(none_stop=True)
