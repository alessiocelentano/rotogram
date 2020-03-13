import json
import re
import urllib

import telebot
from telebot import types
from bs4 import BeautifulSoup


token = open('src/token.txt', 'r').read()
bot = telebot.TeleBot(token)
with open('src/texts.json', 'r') as f:
    t = json.load(f)
with open('dist/pkmn.json', 'r') as f:
    data = json.load(f)


# /--- Functions ---/


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

    evo_text = ''
    family = manage_forms(pkmn_data, 'evolutions')
    if 'from' in family and None not in family['from']:
        evo_text += 'It evolves from <b>{}</b> (<i>{}</i>)\n'.format(
            family['from']['name'],
            family['from']['method']
        )
    if 'into' in family and None not in family['into']:
        if type(family['into']['name']) == list:
            evo = family['into']
            for name, method in zip(evo['name'], evo['method']):
                evo_text += '{} evolves into <b>{}</b> (<i>{}</i>){}'.format(
                    'or' if name != evo['name'][0] else 'It',
                    name,
                    method,
                    '\n' if name == evo['name'][-1] else ' '
                )
        else:
            evo_text += 'It evolves into <b>{}</b> (<i>{}</i>)\n'.format(
                family['into']['name'],
                family['into']['method']
            )
    if not evo_text:
        evo_text = 'It is not known to evolve into or from any other Pokémon\n'

    base_stats = ''
    stats = ['HP', 'Atk', 'Def', 'SpA', 'SpD', 'Spe']
    for base, minn, maxx, stat in zip(
        manage_forms(pkmn_data, 'base_stats').values(),
        manage_forms(pkmn_data, 'min_stats').values(),
        manage_forms(pkmn_data, 'max_stats').values(),
        stats
    ):
        rating = set_rating(int(base))
        base_stats += '<b>{}</b> {} (<i>{}-{}</i>) {}\n'.format(
            base,
            stat,
            minn,
            maxx,
            rating
        )
    legend = t['minmax']

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
            name, artwork, emoji, national,
            typee_str, typee, ab_str, ability,
            evo_text, gender, base_friendship, ev_yield,
            catch_rate, growth_rate, egg_groups, egg_cycles,
            species, height, weight, name_origin,
            other_lang, base_stats, legend
        )
    else:
        text = base_text.format(
            name, artwork, emoji, national,
            typee_str, typee, ab_str, ability,
            evo_text, base_stats, legend
        )
    return text


def set_moveset(pkmn, page):
    maxx = page * 10
    minn = maxx - 9
    index = 0

    text = t['legend'] + '\n\n'
    base_text = '<a href="{}">{}</a> <b>{}</b> ({})\n  \
        <i>{}, {}</i>\n'

    if 'forms' in data[pkmn]:
        form = list(data[pkmn]['forms'].keys())[0]
        moveset = data[pkmn]['forms'][pkmn]['moveset']
        artwork = data[pkmn]['forms'][form]['artwork']
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
            if index >= minn:
                if index <= maxx:
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
                    text += base_text.format(
                        artwork,
                        emoji,
                        name,
                        typee,
                        category,
                        method_text
                    )
    pages = int(index / 10) + 1

    markup = types.InlineKeyboardMarkup(5)
    begin = types.InlineKeyboardButton(
        text='<<1',
        callback_data='moveset/'+pkmn+'/1'
    )
    pre = types.InlineKeyboardButton(
        text=str(page-1),
        callback_data='moveset/'+pkmn+'/'+str(page-1)
    )
    page_button = types.InlineKeyboardButton(
        text='·'+str(page)+'·',
        callback_data='moveset/'+pkmn+'/'+str(page)
    )
    suc = types.InlineKeyboardButton(
        text=str(page+1),
        callback_data='moveset/'+pkmn+'/'+str(page+1)
    )
    end = types.InlineKeyboardButton(
        text=str(pages)+'>>',
        callback_data='moveset/'+pkmn+'/'+str(pages)
    )

    if page == pages:
        markup.add(begin, pre, page_button)
    elif page > 2:
        if page < pages-1:
            markup.add(begin, pre, page_button, suc, end)
        elif page < pages:
            markup.add(begin, pre, page_button, suc)
    elif page > 1:
        if page < pages-1:
            markup.add(pre, page_button, suc, end)
        elif page < pages:
            markup.add(pre, page_button, suc)
    else:
        markup.add(page_button, suc, end)

    return {'text': text, 'markup': markup}


def get_locations(data, pkmn):
    text = ''
    loc_dict = data[pkmn]['location']
    for game, location in loc_dict.items():
        if game == 'firered':
            game = 'Fire Red'
        elif game == 'leafgreen':
            game = 'Leaf Green'
        elif game == 'heartgold':
            game = 'Heart Gold'
        elif game == 'soulsilver':
            game = 'Soul Silver'
        elif game == 'omegaruby':
            game = 'Omega Ruby'
        elif game == 'alphasapphire':
            game = 'Alpha Sapphire'
        elif game == 'letsgopikachu':
            game = 'Let\'s Go, Pikachu!'
        elif game == 'letsgoeevee':
            game = 'Let\'s Go, Eevee!'
        else:
            game = game.title()
        text += '<b>' + game + '</b>: <i>' + location + '</i>\n'
    return text


def get_usage_vgc():
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = 'https://www.smogon.com/stats/'
    request = urllib.request.Request(url, None, headers)
    response = urllib.request.urlopen(request)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')

    link = soup.find_all('a')[-1].attrs['href']
    url = 'https://www.smogon.com/stats/{}gen8vgc2020-1760.txt'.format(link)
    request = urllib.request.Request(url, None, headers)
    response = urllib.request.urlopen(request)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')

    leaderboard = []
    i = 0
    txt = soup.text
    pkmn_list = re.split('\|......\|', txt)
    for pkmn in pkmn_list:
        if pkmn != pkmn_list[0] and pkmn != pkmn_list[1]:
            i += 1
            pkmn = re.sub(' ', '', pkmn)
            stats = re.split('\|', pkmn)
            dictt = {
                'rank': i,
                'pokemon': stats[0],
                'usage': stats[1],
                'raw': stats[2],
                'raw%': stats[3],
                'real': stats[4],
                'real%': stats[5]
            }
            leaderboard.append(dictt)

    return leaderboard


# /--- Bot commands ---/


@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    text = t['start_message']
    bot.send_message(cid, text, parse_mode='HTML')


@bot.callback_query_handler(lambda call: 'basic_infos' in call.data)
@bot.message_handler(commands=['data'])
def pkmn_search(message):
    markup = types.InlineKeyboardMarkup(2)
    try:
        cid = message.message.chat.id
        mid = message.message.message_id
        pkmn = re.split('/', message.data)[1]
        text = set_message(data[pkmn])
        expand = types.InlineKeyboardButton(
            text='➕ Expand',
            callback_data='all_infos/' + pkmn
        )
        moveset = types.InlineKeyboardButton(
            text='⚔️ Moveset',
            callback_data='moveset/' + pkmn
        )
        locations = types.InlineKeyboardButton(
            text='🏠 Locations',
            callback_data='locations/' + pkmn
        )
        markup.add(expand)
        markup.add(moveset, locations)

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
                moveset = types.InlineKeyboardButton(
                    text='⚔️ Moveset',
                    callback_data='moveset/' + pkmn
                )
                locations = types.InlineKeyboardButton(
                    text='🏠 Locations',
                    callback_data='locations/' + pkmn
                )
                markup.add(expand)
                markup.add(moveset, locations)

            else:
                text = t['error2']

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
    locations = types.InlineKeyboardButton(
        text='🏠 Locations',
        callback_data='locations/' + pkmn
    )
    markup.add(reduce, moveset, locations)

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
    if len(re.split('/', call.data)) == 3:
        page = re.split('/', call.data)[2]
    else:
        page = 1
    dictt = set_moveset(pkmn, int(page))

    bot.edit_message_text(
        text=dictt['text'],
        chat_id=cid,
        message_id=mid,
        parse_mode='HTML',
        reply_markup=dictt['markup']
    )


@bot.callback_query_handler(lambda call: 'locations' in call.data)
def locations(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    pkmn = re.split('/', call.data)[1]
    text = get_locations(data, pkmn)
    markup = types.InlineKeyboardMarkup(1)
    info = types.InlineKeyboardButton(
        text='❓ Basic info',
        callback_data='basic_infos/' + pkmn
    )
    moveset = types.InlineKeyboardButton(
        text='⚔️ Moveset',
        callback_data='moveset/' + pkmn
    )

    markup.add(info, moveset)

    bot.edit_message_text(
        text=text,
        chat_id=cid,
        message_id=mid,
        parse_mode='HTML',
        reply_markup=markup
    )


@bot.message_handler(commands=['usage'])
def usage(message):
    cid = message.chat.id
    leaderboard = get_usage_vgc()
    text = ''
    base_text = '''
{}. <b>{}</b>
Usage: <code>{}</code>
Raw: <code>{}</code>
Raw%: <code>{}</code>
Real: <code>{}</code>
Real%: <code>{}</code>
'''
    for i in range(5):
        pkmn = leaderboard[i]
        text += base_text.format(
            i+1,
            pkmn['pokemon'],
            pkmn['usage'],
            pkmn['raw'],
            pkmn['raw%'],
            pkmn['real'],
            pkmn['real%']
        )

    bot.send_message(
        chat_id=cid,
        text=text,
        parse_mode='HTML'
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
