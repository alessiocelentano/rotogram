import json
import re

from pyrogram import Client, Filters
from pyrogram import InlineKeyboardMarkup, InlineKeyboardButton

import functions as func
import raid_dynamax as raid


app = Client(
    session_name='Rotomgram_Beta'
)

texts = json.load(open('src/texts.json', 'r'))
data = json.load(open('src/pkmn.json', 'r'))
stats = json.load(open('src/stats.json', 'r'))

usage_dict = {'vgc': None}
raid_dict = {}


# ===== Bot stats =====
@app.on_message(Filters.text)
def get_bot_data(app, message):
    cid = str(message.chat.id)
    if message.chat.type == 'private':
        stats['users'][cid] = {}
        name = message.chat.first_name
        try:
            name = message.chat.first_name + ' ' + message.chat.last_name
        except TypeError:
            name = message.chat.first_name
        stats['users'][cid]['name'] = name
        try:
            stats['users'][cid]['username'] = message.chat.username
        except AttributeError:
            pass

    elif message.chat.type in ['group', 'supergroup']:
        stats['groups'][cid] = {}
        stats['groups'][cid]['title'] = message.chat.title
        try:
            stats['groups'][cid]['username'] = message.chat.username
        except AttributeError:
            pass

    json.dump(stats, open('src/stats.json', 'w'), indent=4)
    message.continue_propagation()


# ===== Home =====
@app.on_message(Filters.command(['start', 'start@RotomgramBot']))
def start(app, message):
    app.send_message(
        chat_id=message.chat.id,
        text=texts['start_message'],
        parse_mode='HTML'
    )


# ===== Data command =====
@app.on_callback_query(Filters.create(lambda _, query: 'basic_infos' in query.data))
@app.on_message(Filters.command(['data', 'data@RotomgramBot']))
def pkmn_search(app, message):
    try:
        if message.text == '/data' or message.text == '/data@RotomgramBot':
            app.send_message(message.chat.id, texts['error1'], parse_mode='HTML')
            return None
        pkmn = func.find_name(message.text)
        result = func.check_name(pkmn, data)

        if type(result) == str:
            app.send_message(message.chat.id, result)
            return None
        elif type(result) == list:
            best_matches(app, message, result)
            return None
        else:
            pkmn = result['pkmn']
            form = result['form']
    except AttributeError:
        pkmn = re.split('/', message.data)[1]
        form = re.split('/', message.data)[2]


    if pkmn in form:
        text = func.set_message(data[pkmn][form], reduced=True)
    else:
        base_form = re.sub('_', ' ', pkmn.title())
        name = base_form + ' (' + data[pkmn][form]['name'] + ')'
        text = func.set_message(data[pkmn][form], name, reduced=True)

    markup_list = [[
        InlineKeyboardButton(
            text='➕ Expand',
            callback_data='all_infos/'+pkmn+'/'+form
        )
    ],
    [
        InlineKeyboardButton(
            text='⚔️ Moveset',
            callback_data='moveset/'+pkmn+'/'+form
        ),
        InlineKeyboardButton(
            text='🏠 Locations',
            callback_data='locations/'+pkmn+'/'+form
        )
    ]]
    for alt_form in data[pkmn]:
        if alt_form != form:
            markup_list.append([
                InlineKeyboardButton(
                    text=data[pkmn][alt_form]['name'],
                    callback_data='basic_infos/'+pkmn+'/'+alt_form
                )
            ])
    markup = InlineKeyboardMarkup(markup_list)

    func.bot_action(app, message, text, markup)


def best_matches(app, message, result):
    text = texts['results']
    emoji_list = ['1️⃣', '2️⃣', '3️⃣']
    index = 0
    for dictt in result:
        pkmn = dictt['pkmn']
        form = dictt['form']
        percentage = dictt['percentage']
        form_name = data[pkmn][form]['name']
        name = func.form_name(pkmn.title(), form_name)
        text += '\n{} <b>{}</b> (<i>{}</i>)'.format(
            emoji_list[index],
            name,
            percentage
        )
        if index == 0:
            text += ' [<b>⭐️ Top result</b>]'
        index += 1
    app.send_message(message.chat.id, text, parse_mode='HTML')


@app.on_callback_query(Filters.create(lambda _, query: 'all_infos' in query.data))
def all_infos(app, call):
    pkmn = re.split('/', call.data)[1]
    form = re.split('/', call.data)[2]
    
    if pkmn in form:
        text = func.set_message(data[pkmn][form], reduced=False)
    else:
        base_form = re.sub('_', ' ', pkmn.title())
        name = base_form + ' (' + data[pkmn][form]['name'] + ')'
        text = func.set_message(data[pkmn][form], name, reduced=False)

    markup_list = [[
        InlineKeyboardButton(
            text='➖ Reduce',
            callback_data='basic_infos/'+pkmn+'/'+form
        )
    ],
    [
        InlineKeyboardButton(
            text='⚔️ Moveset',
            callback_data='moveset/'+pkmn+'/'+form
        ),
        InlineKeyboardButton(
            text='🏠 Locations',
            callback_data='locations/'+pkmn+'/'+form
        )
    ]]
    for alt_form in data[pkmn]:
        if alt_form != form:
            markup_list.append([
                InlineKeyboardButton(
                    text=data[pkmn][alt_form]['name'],
                    callback_data='basic_infos/'+pkmn+'/'+alt_form
                )
            ])
    markup = InlineKeyboardMarkup(markup_list)

    func.bot_action(app, call, text, markup)


@app.on_callback_query(Filters.create(lambda _, query: 'moveset' in query.data))
def moveset(app, call):
    pkmn = re.split('/', call.data)[1]
    form = re.split('/', call.data)[2]
    if len(re.split('/', call.data)) == 4:
        page = int(re.split('/', call.data)[3])
    else:
        page = 1
    dictt = func.set_moveset(pkmn, form, page)

    func.bot_action(app, call, dictt['text'], dictt['markup'])


@app.on_callback_query(Filters.create(lambda _, query: 'locations' in query.data))
def locations(app, call):
    pkmn = re.split('/', call.data)[1]
    form = re.split('/', call.data)[2]

    text = func.get_locations(data, pkmn)

    markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text='⚔️ Moveset',
            callback_data='moveset/'+pkmn+'/'+form
        )
    ],
    [
        InlineKeyboardButton(
            text='🔙 Back to basic infos',
            callback_data='basic_infos/'+pkmn+'/'+form
        )
    ]])

    func.bot_action(app, call, text, markup)


# ===== Usage command =====
@app.on_callback_query(Filters.create(lambda _, query: 'usage' in query.data))
@app.on_message(Filters.command(['usage', 'usage@RotomgramBot']))
def usage(app, message):
    try:
        page = int(re.split('/', message.data)[1])
        dictt = func.get_usage_vgc(int(page), usage_dict['vgc'])
    except AttributeError:
        page = 1
        text = '<i>Connecting to Pokémon Showdown database...</i>'
        message = app.send_message(message.chat.id, text, parse_mode='HTML')
        dictt = func.get_usage_vgc(int(page))
        usage_dict['vgc'] = dictt['vgc_usage']

    leaderboard = dictt['leaderboard']
    base_text = texts['usage']
    text = ''
    for i in range(15):
        pkmn = leaderboard[i]
        text += base_text.format(
            pkmn['rank'],
            pkmn['pokemon'],
            pkmn['usage'],
        )
    markup = dictt['markup']

    func.bot_action(app, message, text, markup)


# ===== About command =====
@app.on_message(Filters.command(['about', 'about@RotomgramBot']))
def about(app, message):
    text = texts['about']
    markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text='Github',
            url='https://github.com/alessiocelentano/rotomgram'
        )
    ]])

    app.send_message(
        chat_id=message.chat.id,
        text=text, 
        reply_markup=markup
    )


# ===== Raid commands =====
@app.on_message(Filters.command(['addcode', 'addcode@RotomgramBot']))
def call_add_fc(app, message):
    raid.add_fc(app, message, texts)

@app.on_message(Filters.command(['mycode', 'mycode@RotomgramBot']))
def call_show_my_fc(app, message):
    raid.show_my_fc(app, message, texts)

@app.on_message(Filters.command(['newraid', 'newraid@RotomgramBot']))
def call_new_raid(app, message):
    raid.new_raid(app, message, texts)

@app.on_callback_query(Filters.create(lambda _, query: 'stars' in query.data))
def call_stars(app, message):
    raid.stars(app, message, texts)

@app.on_callback_query(Filters.create(lambda _, query: 'join' in query.data))
def call_join(app, message):
    raid.join(app, message, texts)

@app.on_callback_query(Filters.create(lambda _, query: 'done' in query.data))
def call_done(app, message):
    raid.done(app, message, texts)

@app.on_callback_query(Filters.create(lambda _, query: 'yes' in query.data))
def call_confirm(app, message):
    raid.confirm(app, message, texts)

@app.on_callback_query(Filters.create(lambda _, query: 'no' in query.data))
def call_back(app, message):
    raid.back(app, message, texts)

@app.on_callback_query(Filters.create(lambda _, query: 'pin' in query.data))
def call_pin(app, message):
    raid.pin(app, message, texts)


# Presentation
@app.on_message()
def bot_added(app, message):
    if message.new_chat_members:
        for new_member in message.new_chat_members:
            if new_member.id == 932107343:
                text = texts['added']
                app.send_message(
                    chat_id=message.chat.id,
                    text=text
                )
    else:
        message.continue_propagation()


@app.on_message(Filters.command(['stats', 'stats@RotomgramBot']))
def get_stats(app, message):
    if message.from_user.id == 312012637:
        users_text = ''
        for user in stats['users']:
            users_text += stats['users'][user]['name']
            if 'username' in stats['users'][user]:
                users_text += ' (@' + stats['users'][user]['username'] + ')'
            users_text += '\n'

        groups_text = ''
        for group in stats['groups']:
            groups_text += stats['groups'][group]['title']
            if 'username' in stats['groups'][group]:
                groups_text += ' (@' + stats['groups'][group]['username'] + ')'
            groups_text += '\n'

        text = texts['stats'].format(
            len(stats['users']), users_text,
            len(stats['groups']), groups_text
        )
        app.send_message(
            chat_id=message.chat.id,
            text=text
        )


app.run()
