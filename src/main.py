import json
import re

import telebot
from telebot import types


token = open('src/token.txt', 'r').read()
bot = telebot.TeleBot(token)
with open('src/texts.json', 'r') as f:
    t = json.load(f)
with open('dist/pkmn.json', 'r') as f:
    data = json.load(f)


user_dict = {}


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
    if not args:
        base_text = t['reduced_text']
    else:
        base_text = t['expanded_text']
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

    typee = ''
    for i in manage_forms(pkmn_data, 'type').values():
        typee += '/' + i
    typee = typee[1:]
    if '/' in typee:
        typee_str = 'Type'
    else:
        typee_str = 'Types'

    emoji_dict = t['emoji_dict']
    first_type = re.split('/', typee)[0]
    emoji = emoji_dict[first_type]
    name = pkmn_data['name']
    national = pkmn_data['national']
    artwork = manage_forms(pkmn_data, 'artwork')

    if args:
        text = base_text.format(
            name, artwork, emoji,
            national, typee_str, typee,
            ab_str, ability, gender,
            base_friendship, ev_yield, catch_rate,
            growth_rate, egg_groups, egg_cycles,
            species, height, weight,
            name_origin, other_lang, base_stats
        )
    else:
        text = base_text.format(
            name, artwork, emoji,
            national, typee_str, typee,
            ab_str, ability, base_stats
        )
    return text


def set_moveset(pkmn):
    index = 0
    long_moveset = False
    text = t['legend'] + '\n\n'
    text2 = t['legend'] + '\n\n'
    base_text = '<a href="{}">{}</a> <b>{}</b>, {} ({})\n      {}/{}, {}\n\n'
    if 'forms' in data[pkmn]:
        moveset = data[pkmn]['forms'][pkmn]['moveset']
        artwork = data[pkmn]['forms'][pkmn]['artwork']
    else:
        moveset = data[pkmn]['moveset']
        artwork = data[pkmn]['artwork']
    if 'swsh' in moveset:
        moveset = moveset['swsh']
    else:
        moveset = moveset['usum']
    for method, moves in zip(moveset, moveset.values()):
        for move, info in zip(moves, moves.values()):
            index += 1
            name = info['move']
            typee = info['type']
            category = info['cat']
            power = info['power'] if info['power'] is not None else '-'
            accuracy = info['acc'] if info['acc'] is not None else '-'
            emoji = t['emoji_dict'][typee]
            if method == 'level_up':
                method_text = 'Level ' + info['lv']
            elif method == 'tm':
                method_text = 'TM ' + info['tm']
            elif method == 'tr':
                method_text = 'TR ' + info['tr']
            elif method == 'move_tutor':
                method_text = 'Move Tutor'
            elif method == 'hm':
                method_text = 'HM ' + info['hm']
            elif method == 'pre_evo_moves':
                method_text = 'Learned by pre-evolution'
            elif method == 'transfer_only':
                method_text = 'Transfer only'
            elif method == 'egg_moves':
                method_text = 'Egg Move'
            elif method == 'special_moves':
                method_text = 'Special move'
            if index > 70:
                long_moveset = True
                text2 += base_text.format(
                    artwork,
                    emoji,
                    name,
                    typee,
                    category,
                    power,
                    accuracy,
                    method_text
                )
            else:
                text += base_text.format(
                    artwork,
                    emoji,
                    name,
                    typee,
                    category,
                    power,
                    accuracy,
                    method_text
                )
    text += t['legend']
    if long_moveset:
        text2 += t['legend']
        text = [text, text2]
    return text


@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    text = t['start_message']
    bot.send_message(cid, text, parse_mode='HTML')


@bot.callback_query_handler(lambda call: 'basic_infos' in call.data)
@bot.message_handler(commands=['data'])
def pkmn_search(message):
    markup = types.InlineKeyboardMarkup(1)
    try:
        cid = message.message.chat.id
        mid = message.message.message_id
        pkmn = re.split('/', message.data)[1]
        text = set_message(data[pkmn])
        expand = types.InlineKeyboardButton(
            text='➕ Expand',
            callback_data='all_infos/' + pkmn
        )
        markup.add(expand)

    except AttributeError:
        pkmn = find_name(message)
        cid = message.chat.id
        if message.text == '/data':
            text = t['error1']
        else:
            if pkmn in data:
                text = set_message(data[pkmn])
                expand = types.InlineKeyboardButton(
                    text='➕ Expand',
                    callback_data='all_infos/' + pkmn
                )
                markup.add(expand)
            else:
                text = t['error2']
    moveset = types.InlineKeyboardButton(
        text='⚔️ Moveset',
        callback_data='moveset/' + pkmn
    )
    markup.add(moveset)

    try:
        bot.edit_message_text(
            text=text,
            chat_id=cid,
            message_id=mid,
            parse_mode='HTML',
            reply_markup=markup
        )
    except UnboundLocalError:
        bot.send_message(
            chat_id=cid,
            text=text,
            parse_mode='HTML',
            reply_markup=markup
        )


@bot.callback_query_handler(lambda call: 'all_infos' in call.data)
def all_infos(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    pkmn = re.split('/', call.data)[1]
    text = set_message(data[pkmn], True)
    markup = types.InlineKeyboardMarkup(1)
    reduce = types.InlineKeyboardButton(
        text='➖ Reduce',
        callback_data='basic_infos/' + pkmn
    )
    moveset = types.InlineKeyboardButton(
        text='⚔️ Moveset',
        callback_data='moveset/' + pkmn
    )
    markup.add(reduce, moveset)

    bot.edit_message_text(
        text=text,
        chat_id=cid,
        message_id=mid,
        parse_mode='HTML',
        reply_markup=markup
    )


@bot.callback_query_handler(lambda call: 'moveset' in call.data)
def moveset(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    pkmn = re.split('/', call.data)[1]
    text = set_moveset(pkmn)
    markup = types.InlineKeyboardMarkup(1)

    if type(text) == list:
        page2 = types.InlineKeyboardButton(
            text='📃 Page 2 >>',
            callback_data='page2/' + pkmn
        )
        user_dict[mid] = text[1]
        markup.add(page2)
        text = text[0]

    info = types.InlineKeyboardButton(
        text='🏠 Basic info',
        callback_data='basic_infos/' + pkmn
    )
    markup.add(info)

    bot.edit_message_text(
        text=text,
        chat_id=cid,
        message_id=mid,
        parse_mode='HTML',
        reply_markup=markup
    )


@bot.callback_query_handler(lambda call: 'page2' in call.data)
def second_page(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    pkmn = re.split('/', call.data)[1]
    text = user_dict[mid]
    markup = types.InlineKeyboardMarkup(1)
    page1 = types.InlineKeyboardButton(
        text='<< Page 1 📃',
        callback_data='page1/' + pkmn
    )
    markup.add(page1)

    bot.edit_message_text(
        text=text,
        chat_id=cid,
        message_id=mid,
        parse_mode='HTML',
        reply_markup=markup
    )


@bot.message_handler(commands=['about'])
def about(message):
    cid = message.chat.id
    text = t['about']
    markup = types.InlineKeyboardMarkup()
    github = types.InlineKeyboardButton(
        text='Github',
        url='https://github.com/alessiocelentano/Rotomgram'
    )

    markup.add(github)
    bot.send_message(
        chat_id=cid,
        text=text,
        disable_web_page_preview=True,
        reply_markup=markup,
        parse_mode='HTML'
    )


bot.polling(none_stop=True)
