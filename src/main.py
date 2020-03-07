import json
import re

import telebot
from telebot import types


token = open('src/token.txt', 'r').read()
bot = telebot.TeleBot('979765263:AAELCFhUsKZWyjnvwLuAowk8ZNSAHgRxa7k')


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


def set_rating(base):
    rating_n = 0
    rating_emoji = ''
    tiers = [0, 9, 19, 39, 79, 89, 99, 114, 129, 149, 256]
    for i in tiers:
        if base < i:
            while rating_n >= 2:
                rating_emoji += '🌕'
                rating_n -= 2
            if rating_n == 1:
                rating_emoji += '🌗'
            while len(rating_emoji) != 5:
                rating_emoji += '🌑'
            break
        else:
            rating_n += 1
    return rating_emoji


def set_message(pkmn_data, *args):
    if args:
        base_text = '''<b><u>{}</u></b> <a href="{}">{}</a>\n
<b>National</b>: <i>{}</i>
<b>{}</b>: <i>{}</i>
<b>{}</b>: <i>{}</i>\n
<b><u>Games data</u></b>
<b>Gender: </b><i>{}</i>
<b>Base friendship: </b><i>{}</i>
<b>EV yield: </b><i>{}</i>
<b>Catch rate: </b><i>{}</i>
<b>Growth rate: </b><i>{}</i>
<b>Egg groups: </b><i>{}</i>
<b>Egg cycles: </b><i>{}</i>
<b><u>About Pokémon</u></b>
<b>Species: </b><i>{}</i>
<b>Height: </b><i>{}</i>
<b>Weight: </b><i>{}</i>
<b>Name origin: </b><i>{}</i>
<b>Other lang: </b><i>{}</i>\n
<b><u>Base stats</u></b>:
{}
'''

        base_friendship = pkmn_data['base_friendship']
        catch_rate = pkmn_data['catch_rate']
        growth_rate = pkmn_data['growth_rate']
        egg_cycles = pkmn_data['egg_cycles']
        species = pkmn_data['species']

        gender = ''
        for i in pkmn_data['gender']:
            gender += '/' + i
        gender = gender[1:]

        ev_yield = ''
        for i in manage_forms(pkmn_data, 'ev_yield'):
            ev_yield += '/' + i
        ev_yield = ev_yield[1:]

        egg_groups = ''
        for i in pkmn_data['egg_groups']:
            egg_groups += '/' + i
        egg_groups = egg_groups[1:]

        other_lang = ''
        for i, j in pkmn_data['other_lang'].items():
            other_lang += '\n' + i.title() + ': ' + j
        other_lang = other_lang[1:]

        name_origin = ''
        for i, j in pkmn_data['name_origin'].items():
            name_origin += ', ' + i + ' (' + j + ')'
        name_origin = name_origin[2:]

        tmp = manage_forms(pkmn_data, 'height')
        height = tmp['si'] + ' (' + tmp['usc'] + ')'
        tmp = manage_forms(pkmn_data, 'weight')
        weight = tmp['si'] + ' (' + tmp['usc'] + ')'

    else:
        base_text = '''<b><u>{}</u></b> <a href="{}">{}</a>\n
<b>National</b>: <i>{}</i>
<b>{}</b>: <i>{}</i>
<b>{}</b>: <i>{}</i>\n
<b><u>Base stats</u></b>:
{}
'''

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
    typee = ''
    for i in manage_forms(pkmn_data, 'type').values():
        typee += '/' + i
    typee = typee[1:]
    if '/' in typee:
        typee_str = 'Type'
    else:
        typee_str = 'Types'
    first_type = re.split('/', typee)[0]
    emoji = emoji_dict[first_type]

    name = pkmn_data['name']
    national = pkmn_data['national']
    artwork = manage_forms(pkmn_data, 'artwork')

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
        rating = set_rating(int(base))
        base_stats += '<b>' + base + '</b> ' + stat + ' ' + rating + '\n'

    if args:
        text = base_text.format(
            name,
            artwork,
            emoji,
            national,
            typee_str,
            typee,
            ab_str,
            ability,
            gender,
            base_friendship,
            ev_yield,
            catch_rate,
            growth_rate,
            egg_groups,
            egg_cycles,
            species,
            height,
            weight,
            name_origin,
            other_lang,
            base_stats,
        )
    else:
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
but I still can't read in thought. Use this syntax: \
<code>/data + PokémonName</code>
ex.: <code>/data Rotom</code>
'''
    else:
        with open('dist/pkmn.json', 'r') as f:
            data = json.load(f)
        if pkmn in data:
            text = set_message(data[pkmn])
            markup = types.InlineKeyboardMarkup()
            expand = types.InlineKeyboardButton(
                text='➕ Expand',
                callback_data='all_infos/' + pkmn
            )
            markup.add(expand)

        else:
            text = '''
Mm-hmm, well, maybe he's an anime character, but he certainly \
izzn't a Pokémon. Zzzt-zzt! ⚡️
'''

    bot.send_message(cid, text, parse_mode='HTML', reply_markup=markup)


@bot.callback_query_handler(lambda call: 'all_infos' in call.data)
def all_infos(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    pkmn = re.split('/', call.data)[1]
    with open('dist/pkmn.json', 'r') as f:
        data = json.load(f)
    text = set_message(data[pkmn], True)
    markup = types.InlineKeyboardMarkup()
    reduce = types.InlineKeyboardButton(
        text='➖ Reduce',
        callback_data='basic_infos'
    )
    markup.add(reduce)

    bot.edit_message_text(
        text=text,
        chat_id=cid,
        message_id=mid,
        parse_mode='HTML',
        reply_markup=markup
    )


bot.polling(none_stop=True)
