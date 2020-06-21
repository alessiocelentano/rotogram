import json
import re
import random

from pyrogram import InlineKeyboardMarkup, InlineKeyboardButton

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


def add_fc(app, message, texts):
    data = json.load(open('src/friendcodes.json', 'r'))
    user = message.from_user.first_name
    cid = str(message.chat.id)
    uid = str(message.from_user.id)

    if len(re.split('\s', message.text)) == 1:
        text = texts['incomplete_fc_error']
        app.send_message(cid, text, parse_mode='HTML')
        return True

    fc = re.search('(SW(-|\s)*)*([0-9]{4}(-|\s)*){2}[0-9]{4}', message.text)

    if not fc:
        text = texts["fc_error"]
        app.send_message(cid, text, parse_mode='HTML')
        return None

    else:
        fc = re.sub('(SW)|\s|-', '', fc[0])
        blocks = re.findall('[0-9]{4}', fc)
        fc = '-'.join(blocks)
        data[uid] = {'fc': fc, 'user': user}
        if uid in data:
            text = texts['fc_update'].format(user, fc)
        else:
            text = texts['fc_add'].format(user, fc)
        app.send_message(cid, text, parse_mode='HTML')
        with open('src/friendcodes.json', 'w') as filee:
            json.dump(data, filee, indent=4)


def show_my_fc(app, message, texts):
    data = json.load(open('src/friendcodes.json', 'r'))
    user = message.from_user.first_name
    cid = str(message.chat.id)
    uid = str(message.from_user.id)

    if uid in data:
        text = data[uid]['fc']
    else:
        text = texts['no_fc']

    app.send_message(cid, text, parse_mode='HTML')


def new_raid(app, message, texts):
    data = json.load(open('src/friendcodes.json', 'r'))
    user = message.from_user.first_name
    cid = str(message.chat.id)
    uid = str(message.from_user.id)
    raid = Raid()
    user_dict[uid] = raid

    if message.chat.type == 'private':
        text = texts['not_available']
        app.send_message(cid, text, parse_mode='HTML')
        return True
    if len(re.split('\s', message.text)) == 1:
        text = texts['new_raid_error']
        app.send_message(cid, text, parse_mode='HTML')
        return True

    raid.pokemon = re.sub('\/newraid(@RotomgramBot)*\s', '', message.text)
    if uid in data:
        raid.fc = data[uid]['fc']
    else:
        raid.fc = '-'
    raid.idd = uid
    raid.owner = user
    raid.players = []
    text = texts['new_raid'].format(
        raid.pokemon,
        raid.owner,
        raid.fc,
        raid.players[0] if len(raid.players) > 0 else '-',
        raid.players[1] if len(raid.players) > 1 else '-',
        raid.players[2] if len(raid.players) > 2 else '-',
    )

    markup_list = [[]]
    for i in range(1, 6):
        markup_list[-1].append(
            InlineKeyboardButton(
                text=str(i)+'⭐️',
                callback_data=str(raid.idd)+'stars'+str(i)
            )
        )
    markup_list.append([
        InlineKeyboardButton(
            text='🙋‍♂️ Join',
            callback_data='join'+str(raid.idd)
        ),
        InlineKeyboardButton(
            text='🚫 Close',
            callback_data='done'+str(raid.idd)
        )
    ])
    markup = InlineKeyboardMarkup(markup_list)

    app.send_message(cid, text, parse_mode='HTML', reply_markup=markup)


def stars(app, call, texts):
    data = json.load(open('src/friendcodes.json', 'r'))
    cid = str(call.message.chat.id)
    uid = str(call.from_user.id)
    mid = call.message.message_id
    owner_uid = re.findall('[0-9]+', call.data)[0]
    raid = user_dict[owner_uid]

    if uid != raid.idd:
        text = texts['not_creator']
        app.answer_callback_query(call.id, text, True)
        return None

    raid.stars = '⭐️' * int(call.data[-1])

    text = texts['new_raid'].format(
        raid.pokemon + ' ' + raid.stars,
        raid.owner,
        raid.fc,
        raid.players[0] if len(raid.players) > 0 else '-',
        raid.players[1] if len(raid.players) > 1 else '-',
        raid.players[2] if len(raid.players) > 2 else '-',
    )

    markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text='🙋‍♂️ Join',
            callback_data='join'+str(raid.idd)
        ),
        InlineKeyboardButton(
            text='🚫 Close',
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
    data = json.load(open('src/friendcodes.json', 'r'))
    cid = str(call.message.chat.id)
    uid = str(call.from_user.id)
    mid = call.message.message_id
    user = call.from_user.first_name
    owner_uid = re.findall('[0-9]+', call.data)[0]
    raid = user_dict[owner_uid]
        
    if uid == raid.idd:
        return None

    if len(raid.players) == 3:
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
        raid.players[0] if len(raid.players) > 0 else '-',
        raid.players[1] if len(raid.players) > 1 else '-',
        raid.players[2] if len(raid.players) > 2 else '-',
    )

    markup_list = []
    if raid.stars == None:
        markup_list.append([])
        for i in range(1, 6):
            markup_list[-1].append(
                InlineKeyboardButton(
                    text=str(i)+'⭐️',
                    callback_data=str(raid.idd)+'stars'+str(i)
                )
            )
    markup_list.append([
        InlineKeyboardButton(
            text='🙋‍♂️ Join',
            callback_data='join'+str(raid.idd)
        ),
        InlineKeyboardButton(
            text='🚫 Close',
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
    data = json.load(open('src/friendcodes.json', 'r'))
    cid = str(call.message.chat.id)
    uid = str(call.from_user.id)
    mid = call.message.message_id
    user = call.from_user.first_name
    owner_uid = re.findall('[0-9]+', call.data)[0]
    raid = user_dict[owner_uid]

    if uid != raid.idd:
        app.answer_callback_query(call.id, texts['not_creator'], True)
        return None

    markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text='✅ Confirm',
            callback_data='yes'+str(raid.idd)
        ),
        InlineKeyboardButton(
            text='◀️ Back',
            callback_data='no'+str(raid.idd))
    ]])

    app.edit_message_reply_markup(
        chat_id=cid,
        message_id=mid,
        reply_markup=markup
    )


def confirm(app, call, texts):
    data = json.load(open('src/friendcodes.json', 'r'))
    cid = str(call.message.chat.id)
    uid = str(call.from_user.id)
    mid = call.message.message_id
    owner_uid = re.findall('[0-9]+', call.data)[0]
    raid = user_dict[owner_uid]

    if uid != raid.idd:
        app.answer_callback_query(call.id, texts['not_creator'], True)
        return None
        
    text = texts['new_raid'].format(
        raid.pokemon + ' ' + raid.stars if raid.stars else raid.pokemon,
        raid.owner,
        raid.fc,
        raid.players[0] if len(raid.players) > 0 else '-',
        raid.players[1] if len(raid.players) > 1 else '-',
        raid.players[2] if len(raid.players) > 2 else '-',
    )

    text += texts['raid_closed']

    pin = ''
    for i in range(4):
        pin += random.choice('0123456789')
    raid.pin = pin

    markup = InlineKeyboardMarkup([[
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
    data = json.load(open('src/friendcodes.json', 'r'))
    cid = str(call.message.chat.id)
    uid = str(call.from_user.id)
    mid = call.message.message_id
    owner_uid = re.findall('[0-9]+', call.data)[0]
    raid = user_dict[owner_uid]
        
    if uid != raid.idd:
        app.answer_callback_query(call.id, texts['not_creator'], True)
        return None

    text = texts['new_raid'].format(
        raid.pokemon + ' ' + raid.stars if raid.stars else raid.pokemon,
        raid.owner,
        raid.fc,
        raid.players[0] if len(raid.players) > 0 else '-',
        raid.players[1] if len(raid.players) > 1 else '-',
        raid.players[2] if len(raid.players) > 2 else '-',
    )

    markup_list = []
    if raid.stars == None:
        markup_list.append([])
        for i in range(1, 6):
            markup_list[-1].append(
                InlineKeyboardButton(
                    text=str(i)+'⭐️',
                    callback_data=str(raid.idd)+'stars'+str(i)
                )
            )
    markup_list.append([
        InlineKeyboardButton(
            text='🙋‍♂️ Join',
            callback_data='join'+str(raid.idd)
        ),
        InlineKeyboardButton(
            text='🚫 Close',
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
    data = json.load(open('src/friendcodes.json', 'r'))
    uid = str(call.from_user.id)
    owner_uid = re.findall('[0-9]+', call.data)[0]
    raid = user_dict[owner_uid]

    if uid in raid.players_id or uid == owner_uid: 
        app.answer_callback_query(call.id, raid.pin, True)
    else:
        app.answer_callback_query(call.id, texts["not_player"], True)
