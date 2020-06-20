import json
import re
import random

from pyrogram import InlineKeyboardMarkup, InlineKeyboardInline

import functions as func


user_dict = {}


class Raid():
    def __init__(self):
        self.idd = None
        self.pokemon = None
        self.stars = None
        self.owner = None
        self.fc = None
        self.players = []
        self.players_id = []
        self.pin = None


def check_invalid_input(app, message):
    if message.chat.type == 'private':
        text = texts['not_available']
        app.send_message(cid, text, parse_mode='HTML')
        return True

    if message.text == '/(.)+@RotomgramBot':
        text = texts["incomplete_fc_error"].format(user)
        app.send_message(cid, text, parse_mode='HTML')
        return True


def add_fc(app, message, texts):
    if check_invalid_input(app, message):
        return None

    data = json.load(open('friendcodes.json', 'r'))
    user = message.from_user.first_name
    cid = str(message.chat.id)
    uid = str(message.from_user.id)

    fc = re.findall('(SW-)*([0-9]{4}(-)*{3}', message.text)[0]

    if not fc:
        text = texts["fc_error"].format(user)
        app.send_message(cid, text, parse_mode='HTML')
        return None

    else:
        fc = re.sub('SW-|\s', '', fc)
        data[uid] = {'fc': fc, 'user': user}
        if uid in data:
            text = texts['fc_update'].format(user, fc)
        else:
            text = texts['fc_add'].format(user, fc)
        app.send_message(cid, text, parse_mode='HTML')
        with open('friendcodes.json', 'w') as filee:
            json.dump(data, filee, indent=4)


def show_fc(app, message, texts):
    if check_invalid_input(app, message):
        return None

    data = json.load(open('friendcodes.json', 'r'))
    cid = str(message.chat.id)
    uid = str(message.from_user.id)

    fc_list = ''
    for idd in data:
        fc = data[idd]['fc']
        user = data[idd]['user']
        fc_list += fc + ': ' + user + '\n' 

    if fc_list:
        text = texts['fc_list'] + fc_list
    else:
        text = texts['no_fcs']

    app.send_message(cid, text, parse_mode='HTML')


def show_my_fc(app, message, texts):
    if check_invalid_input(app, message):
        return None

    data = json.load(open('friendcodes.json', 'r'))
    cid = str(message.chat.id)
    uid = str(message.from_user.id)

    if uid in data:
        text = data[cid]['fc']
    else:
        text = texts['no_fc']

    app.send_message(cid, text, parse_mode='HTML')


def new_raid(app, message, texts):
    if check_invalid_input(app, message):
        return None

    data = json.load(open('friendcodes.json', 'r'))
    cid = str(message.chat.id)
    uid = str(message.from_user.id)
    user = message.from_user.first_name
    raid = Raid()
    user_dict[message.from_user.id] = raid

    raid.pokemon = re.sub('/new(@RotomgramBot)* ', message.text)
    if not raid.pokemon:
        text = texts['new_raid_error'].format(user)
        app.send_message(cid, text, parse_mode='HTML')
        return None

    else:
        if uid in data:
            raid.fc = data[uid]['fc']
        else:
            raid.fc = '-'
        raid.idd = uid
        raid.owner = user
        raid.players = ['-', '-', '-']
        text = texts['new_raid'].format(
            raid.pokemon,
            raid.owner,
            raid.fc,
            raid.players[0],
            raid.players[1],
            raid.players[2]
        )

        markup_list = [[]]
        for i in range(1, 5):
            markup_list[-1].append(
                InlineKeyboardButton(
                    text=i+'⭐️',
                    callback_data=i+'stars'
                )
            )
        markup_list.append([
            InlineKeyboardButton(
                text='Join',
                callback_data='join'+str(raid.idd)
            ),
            InlineKeyboardButton(
                text='Close',
                callback_data='done'+str(raid.idd)
            )
        ])
        markup = InlineKeyboardMarkup(markup_list)

        app.send_message(cid, text, parse_mode='HTML', reply_markup=markup)


def stars(app, call, texts):
    data = json.load(open('friendcodes.json', 'r'))
    cid = (call.message.chat.id)
    uid = (call.from_user.id)
    mid = (call.message.message_id)
    owner_uid = re.findall('[0-9]+', call.data)[0]
    raid = user_dict[owner_id]

    if uid != raid.idd:
        text = texts['not_creator']
        app.answer_callback_query(call.id, text, True)
        return None

    raid.stars = '⭐️' * call.data[0]

    text = texts['new_raid'].format(
        raid.pokemon + ' ' + raid.stars,
        raid.owner,
        raid.fc,
        raid.players[0],
        raid.players[1],
        raid.players[2]
    )

    markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text='Join',
            callback_data='join'+str(raid.idd)
        ),
        InlineKeyboardButton(
            text='Close',
            callback_data='done'+str(raid.idd)
        )
    ]])

    app.edit_message_text(
        chat_id=cid,
        message_id=mid,
        text=text,
        parse_mode='HTML',
        reply_markup=markup
    )


def join(app, call, texts):
    data = json.load(open('friendcodes.json', 'r'))
    cid = str(call.message.chat.id)
    uid = str(call.from_user.id)
    mid = str(call.message.message_id)
    user = call.from_user.first_name
    owner_uid = re.findall('[0-9]+', call.data)[0]
    raid = user_dict[owner_uid]
        
    if user == raid.owner:
        return None

    if len(raid.players) > 3:
        text = 'Full Raid'
        app.answer_callback_query(call.id, text, True)
        return None

    if uid not in raid.players_id:
        raid.players.append(user)
        raid.players_id.append(uid)
    else:
        raid.players.remove(user)
        raid.players_id.remove(uid)

    text = texts['new_raid'].format(
        raid.pokemon + ' ' + raid.stars if raid.stars else raid.pokemon,
        raid.owner,
        raid.fc,
        players[0],
        players[1],
        players[2]
    )

    markup_list = []
    if raid.stars == None:
        markup_list.append([])
        for i in range(1, 5):
            markup_list[-1].append(
                InlineKeyboardButton(
                    text=i+'⭐️',
                    callback_data=i+'stars'
                )
            )
    markup_list.append([
        InlineKeyboardButton(
            text='Join',
            callback_data='join'+str(raid.idd)
        ),
        InlineKeyboardButton(
            text='Close',
            callback_data='done'+str(raid.idd)
        )
    ])
    markup = InlineKeyboardMarkup(markup_list)

    app.edit_message_text(
        chat_id=cid,
        message_id=mid,
        text=text,
        parse_mode='HTML',
        reply_markup=markup
    )


def done(app, call, texts):
    data = json.load(open('friendcodes.json', 'r'))
    cid = str(call.message.chat.id)
    uid = str(call.from_user.id)
    mid = str(call.message.message_id)
    user = call.from_user.first_name
    raid = user_dict[int(call.data.replace('done', ''))]

    if uid != raid.idd:
        app.answer_callback_query(call.id, texts['not_creator'], True)
        return None

    markup = types.InlineKeyboardMarkup([[
        InlineKeyboardButton(
            texts['confirm'],
            callback_data='yes'+str(raid.idd)
        ),
        InlineKeyboardButton(
            texts['back'],
            callback_data='no'+str(raid.idd))
    ]])

    app.edit_message_reply_markup(
        chat_id=cid,
        message_id=mid,
        reply_markup=markup
    )


def confirm(app, call, texts):
    data = json.load(open('friendcodes.json', 'r'))
    cid = str(call.message.chat.id)
    mid = str(call.message.message_id)
    owner_uid = re.findall('[0-9]+', call.data)[0]
    raid = user_dict[owner_uid]

    if uid != raid.idd:
        app.answer_callback_query(call.id, texts['not_creator'], True)
        return None
        
    text = texts['new_raid'].format(
        raid.pokemon + ' ' + raid.stars if raid.stars else raid.pokemon,
        raid.owner,
        raid.fc,
        players[0],
        players[1],
        players[2]
    )

    text += texts['raid_closed']

    pin = ''
    for i in range(4):
        pin += random.choice('0123456789')
    raid.pin = pin

    markup = types.InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text='Pin',
            callback_data='pin'+str(raid.idd)
        )
    ]])

    app.edit_message_text(
        chat_id=cid,
        message_id=mid,
        text=text,
        parse_mode='HTML',
        reply_markup=markup
    )


def back(app, call, texts):
    data = json.load(open('friendcodes.json', 'r'))
    cid = str(call.message.chat.id)
    mid = str(call.message.message_id)
    raid = user_dict[int(call.data.replace('no', ''))]
        
    if call.from_user.id != raid.idd:
        app.answer_callback_query(call.id, texts['not_creator'], True)
        return None

    text = texts['new_raid'].format(
        raid.pokemon + ' ' + raid.stars if raid.stars else raid.pokemon,
        raid.owner,
        raid.fc,
        players[0],
        players[1],
        players[2]
    )

    markup_list = []
    if raid.stars == None:
        markup_list.append([])
        for i in range(1, 5):
            markup_list[-1].append(
                InlineKeyboardButton(
                    text=i+'⭐️',
                    callback_data=i+'stars'
                )
            )
    markup_list.append([
        InlineKeyboardButton(
            text='Join',
            callback_data='join'+str(raid.idd)
        ),
        InlineKeyboardButton(
            text='Close',
            callback_data='done'+str(raid.idd)
        )
    ])
    markup = InlineKeyboardMarkup(markup_list)

    app.edit_message_text(
        chat_id=cid,
        message_id=mid,
        text=text,
        parse_mode='HTML',
        reply_markup=markup
    )


def pin(app, call, texts):
    data = json.load(open('friendcodes.json', 'r'))
    uid = str(call.from_user.id)
    owner_uid = re.findall('[0-9]+')[0]
    raid = user_dict[owner_uid]

    if uid in raid.players_id or uid == owner_uid: 
        app.answer_callback_query(call.id, raid.pin, True)
    else:
        app.answer_callback_query(call.id, texts["not_player"], True)


def credits(app, message, texts):
    if check_invalid_input(app, message):
        return None
    cid = message.chat.id

    text = texts['credits']

    app.send_message(
        chat_id=cid,
        text=text
    )
