import json
import re

import telebot
from telebot import types

from functions import *


token = open('src/token.txt', 'r').read()
bot = telebot.TeleBot('979765263:AAFQ41JFJBp9ghT4SP6hhtE4OnRDyQGNfkk')
with open('src/texts.json', 'r') as f:
    t = json.load(f)
with open('dist/pkmn.json', 'r') as f:
    data = json.load(f)


# It's updated when /usage command is used
# When inline buttons are used, get usage from this list
usage_dict = {'vgc': None}


@bot.message_handler(commands=['start'])
def start(message):
    """Simply the start command"""

    cid = message.chat.id
    text = t['start_message']
    bot.send_message(cid, text, parse_mode='HTML')


@bot.callback_query_handler(lambda call: 'basic_infos' in call.data)
@bot.message_handler(commands=['data'])
def pkmn_search(message):
    """It shows basic information about the Pokémon"""

    markup = types.InlineKeyboardMarkup(2)
    try:
        # Run this if a button is pressed
        cid = message.message.chat.id
        mid = message.message.message_id
        pkmn = re.split('/', message.data)[1]
        form = re.split('/', message.data)[2]

        if pkmn in form:
            # For readibility
            # e.g.: Mega Charizard X has Charizard in the name
            #       so it's understandable
            text = set_message(data[pkmn][form])
        else:
            # e.g.: Low Key Form isn't clear (It's a Toxtricity form)
            #       in this case, it returns "Toxtricity (Low key Form)"
            base_form = re.sub('_', ' ', pkmn.title())
            name = base_form + ' (' + data[pkmn][form]['name'] + ')'
            text = set_message(data[pkmn][form], name)

        expand = types.InlineKeyboardButton(
            text='➕ Expand',
            callback_data='all_infos/'+pkmn+'/'+form
        )
        moveset = types.InlineKeyboardButton(
            text='⚔️ Moveset',
            callback_data='moveset/'+pkmn+'/'+form
        )
        locations = types.InlineKeyboardButton(
            text='🏠 Locations',
            callback_data='locations/'+pkmn+'/'+form
        )
        markup.add(expand)
        markup.add(moveset, locations)

        for alt_form in data[pkmn]:
            if alt_form != form:
                form_button = types.InlineKeyboardButton(
                    text=data[pkmn][alt_form]['name'],
                    callback_data='basic_infos/'+pkmn+'/'+alt_form
                )
                markup.add(form_button)

    except AttributeError:
        # Run this if /data is used
        pkmn = find_name(message.text)
        cid = message.chat.id
        if message.text == '/data':
            text = t['error1']
        else:
            result = check_name(pkmn, data)
            if type(result) == str:
                # Invalid input: 25 characters limit exceeded
                text = result

            elif 'pkmn' in result:
                # Valid input: return Pokémon infocard
                pkmn = result['pkmn']
                form = result['form']
                if pkmn in form:
                    # For readibility
                    # e.g.: Mega Charizard X has Charizard in the name
                    #       so it's understandable
                    text = set_message(data[pkmn][form])
                else:
                    # e.g.: Low Key Form isn't clear (It's a Toxtricity form)
                    #       in this case, it returns "Toxtricity (Low key Form)"
                    base_form = re.sub('_', ' ', pkmn.title())
                    name = base_form + ' (' + data[pkmn][form]['name'] + ')'
                    text = set_message(data[pkmn][form], name)

                expand = types.InlineKeyboardButton(
                    text='➕ Expand',
                    callback_data='all_infos/'+pkmn+'/'+form
                )
                moveset = types.InlineKeyboardButton(
                    text='⚔️ Moveset',
                    callback_data='moveset/'+pkmn+'/'+form
                )
                locations = types.InlineKeyboardButton(
                    text='🏠 Locations',
                    callback_data='locations/'+pkmn+'/'+form
                )
                markup.add(expand)
                markup.add(moveset, locations)
                # If Pokémon has alternative forms, it creates its button
                for alt_form in data[pkmn]:
                    if alt_form != form:
                        form_button = types.InlineKeyboardButton(
                            text=data[pkmn][alt_form]['name'],
                            callback_data='basic_infos/'+pkmn+'/'+alt_form
                        )
                        markup.add(form_button)
            else:
                # Invalid input: it returns 3 best matches
                text = t['results']
                index = 1
                for pkmn, form, percent in result:
                    form = data[pkmn][form]['name']
                    name = form_name(pkmn.title(), form)
                    if index == 1:
                        n = '1️⃣'
                    elif index == 2:
                        n = '2️⃣'
                    else:
                        n = '3️⃣'
                    text += '\n' + n + ' <b>' + name + '</b> (<i>' + percent + '</i>)'
                    if index == 1:
                        text += ' [<b>⭐️ Top result</b>]'
                    index += 1

    try:
        # Buttons
        
        # It interrupt button loading circle
        bot.answer_callback_query(message.id)
        bot.edit_message_text(
            text=text,
            chat_id=cid,
            message_id=mid,
            parse_mode='HTML',
            reply_markup=markup
        )
    except UnboundLocalError:
        # Command
        bot.send_message(
            chat_id=cid,
            text=text,
            parse_mode='HTML',
            reply_markup=markup
        )


@bot.callback_query_handler(lambda call: 'all_infos' in call.data)
def all_infos(call):
    """Show all information about the Pokémon by pressing "Expand" button"""

    cid = call.message.chat.id
    mid = call.message.message_id
    pkmn = re.split('/', call.data)[1]
    form = re.split('/', call.data)[2]
    
    if pkmn in form:
        # For readibility
        # e.g.: Mega Charizard X has Charizard in the name
        #       so it's understandable
        text = set_message(data[pkmn][form], True)
    else:
        # e.g.: Low Key Form isn't clear (It's a Toxtricity form)
        #       in this case, it returns "Toxtricity (Low key Form)"
        base_form = re.sub('_', ' ', pkmn.title())
        name = base_form + ' (' + data[pkmn][form]['name'] + ')'
        text = set_message(data[pkmn][form], True, name)

    markup = types.InlineKeyboardMarkup(2)
    reduce = types.InlineKeyboardButton(
        text='➖ Reduce',
        callback_data='basic_infos/'+pkmn+'/'+form
    )
    moveset = types.InlineKeyboardButton(
        text='⚔️ Moveset',
        callback_data='moveset/'+pkmn+'/'+form
    )
    locations = types.InlineKeyboardButton(
        text='🏠 Locations',
        callback_data='locations/'+pkmn+'/'+form
    )
    markup.add(reduce)
    markup.add(moveset, locations)

    bot.answer_callback_query(call.id) # It interrupt button loading circle
    bot.edit_message_text(
        text=text,
        chat_id=cid,
        message_id=mid,
        parse_mode='HTML',
        reply_markup=markup
    )


@bot.callback_query_handler(lambda call: 'moveset' in call.data)
def moveset(call):
    """Show Pokémon moveset"""

    cid = call.message.chat.id
    mid = call.message.message_id
    pkmn = re.split('/', call.data)[1]
    form = re.split('/', call.data)[2]
    if len(re.split('/', call.data)) == 4:
        page = re.split('/', call.data)[3]
    else:
        page = 1
    dictt = set_moveset(pkmn, form, int(page))

    bot.answer_callback_query(call.id) # It interrupt button loading circle
    bot.edit_message_text(
        text=dictt['text'],
        chat_id=cid,
        message_id=mid,
        parse_mode='HTML',
        reply_markup=dictt['markup']
    )


@bot.callback_query_handler(lambda call: 'locations' in call.data)
def locations(call):
    """Show Pokémon location in each core game"""

    cid = call.message.chat.id
    mid = call.message.message_id
    pkmn = re.split('/', call.data)[1]
    form = re.split('/', call.data)[2]
    text = get_locations(data, pkmn)
    markup = types.InlineKeyboardMarkup(1)
    moveset = types.InlineKeyboardButton(
        text='⚔️ Moveset',
        callback_data='moveset/'+pkmn+'/'+form
    )
    info = types.InlineKeyboardButton(
        text='🔙 Back to basic infos',
        callback_data='basic_infos/'+pkmn+'/'+form
    )
    markup.add(moveset, info)

    bot.answer_callback_query(call.id) # It interrupt button loading circle
    bot.edit_message_text(
        text=text,
        chat_id=cid,
        message_id=mid,
        parse_mode='HTML',
        reply_markup=markup
    )


@bot.callback_query_handler(lambda call: 'usage' in call.data)
@bot.message_handler(commands=['usage'])
def usage(message):
    """Show usage leaderboard"""

    try:
        # Buttons
        cid = message.message.chat.id
        mid = message.message.message_id
        page = re.split('/', message.data)[1]
        dictt = get_usage_vgc(int(page), usage_dict['vgc'])

    except AttributeError:
        # Command
        cid = message.chat.id
        page = 1
        msg = bot.send_message(
            chat_id=cid,
            text='<i>Connecting to Pokémon Showdown database...</i>',
            parse_mode='HTML'
        )
        mid = msg.message_id
        dictt = get_usage_vgc(int(page))
        usage_dict['vgc'] = dictt['vgc_usage']

    leaderboard = dictt['leaderboard']
    markup = dictt['markup']
    text = ''
    base_text = '{}. <b>{}</b> (<i>{}</i>)\n'

    for i in range(15):
        pkmn = leaderboard[i]
        text += base_text.format(
            pkmn['rank'],
            pkmn['pokemon'],
            pkmn['usage'],
        )

    try:
        # It interrupt button loading circle
        bot.answer_callback_query(message.id)
    except AttributeError:
        pass
    bot.edit_message_text(
        text=text,
        chat_id=cid,
        message_id=mid,
        parse_mode='HTML',
        reply_markup=markup
    )


@bot.message_handler(commands=['about'])
def about(message):
    """About the Pokémon"""

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
