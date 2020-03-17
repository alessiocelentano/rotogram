import json
import re
import urllib

import telebot
from telebot import types
from bs4 import BeautifulSoup


token = open('src/token.txt', 'r').read()
bot = telebot.TeleBot('979765263:AAFQ41JFJBp9ghT4SP6hhtE4OnRDyQGNfkk')
with open('src/texts.json', 'r') as f:
    t = json.load(f)
with open('dist/pkmn.json', 'r') as f:
    data = json.load(f)


# It's updated when /usage command is used
# When inline buttons are used, get usage from this list
usage_dict = {'vgc': None}


# /--- Functions ---/


def find_name(pkmn):
    """Convert input in a valid format for JSON"""

    pkmn = pkmn.lower()
    pkmn = re.sub('♀', '-f', pkmn)  # For Nidoran♀
    pkmn = re.sub('♂', '-m', pkmn)  # For Nidoran♂
    pkmn = re.sub('[èé]', 'e', pkmn)  # For Flabébé
    pkmn = re.sub('/data(@RotomgramBot|) ', '', pkmn)
    pkmn = re.sub(' ', '-', pkmn)
    pkmn = re.sub('[^a-z-]', '', pkmn)
    return pkmn


def set_message(pkmn, *args):
    """Set Home message"""

    def set_rating(base):
        """Create a legend with moon emoticons
        The higher the statistic, the more full moons there will be
        """

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

    if not args:
        base_text = t['reduced_text']

    else:
        # If True is passed in set_message, it returns all informations
        # Below, convert JSON additional data in user-friendly message
        base_text = t['expanded_text']
        base_friendship = pkmn['base_friendship']['value']
        catch_rate = pkmn['catch_rate']['value']
        growth_rate = pkmn['growth_rate']
        egg_cycles = pkmn['egg_cycles']
        species = pkmn['species']

        gender = ''
        if pkmn['gender']['genderless']:
            gender += 'Genderless'
        else:
            for i, j in list(pkmn['gender'].items()):
                if j == '100%':
                    gender = i + ': ' + j + '\n'
                elif type(j) == bool:
                    continue
                else:
                    gender += i + ': ' + j + '\n'
            gender = gender[:-1]

        ev_yield = ''
        for i in pkmn['ev_yield']:
            ev_yield += ' / ' + pkmn['ev_yield'][i] + ' ' + i.title()
        ev_yield = ev_yield[3:]

        egg_groups = ''
        for i in pkmn['egg_groups']:
            egg_groups += ' / ' + i
        egg_groups = egg_groups[3:]

        other_lang = ''
        for i, j in pkmn['other_lang'].items():
            other_lang += '\n' + i.title() + ': ' + j
        other_lang = other_lang[1:]

        name_origin = ''
        for i, j in pkmn['name_origin'].items():
            name_origin += ', ' + i + ' (' + j + ')'
        name_origin = name_origin[2:]

        tmp = pkmn['height']
        height = tmp['si'] + ' (' + tmp['usc'] + ')'
        tmp = pkmn['weight']
        weight = tmp['si'] + ' (' + tmp['usc'] + ')'

    # Convert JSON base data in user-friendly message
    ability = ''
    for i, j in pkmn['abilities'].items():
        if i == 'hidden_ability':
            ability += '\n' + '<b>Hidden Ability</b>: ' + j
        else:
            ability += ' / ' + j
    ability = ability[3:]
    if '/' in ability:
        ab_str = 'Abilities'
    else:
        ab_str = 'Ability'

    evo_text = ''
    family = pkmn['evolutions']
    if family:
        if None not in family['from'].values():
            evo_text += 'It evolves from <b>{}</b> (<i>{}</i>)\n'.format(
                family['from']['name'],
                family['from']['method']
            )
        if None not in family['into'].values():
            if type(family['into']['name']) == list:
                evo = family['into']
                for name, method in zip(evo['name'], evo['method']):
                    if name == evo['name'][0]:
                        intro_text = 'It evolves'
                    elif name == evo['name'][-1]:
                        intro_text = 'or'
                    else:
                        intro_text = ','
                    evo_text += '{} into <b>{}</b> (<i>{}</i>){}'.format(
                        intro_text,
                        name,
                        method,
                        '\n' if name == evo['name'][-1] else ' '
                    )
            else:
                evo_text += 'It evolves into <b>{}</b> (<i>{}</i>)\n'.format(
                    family['into']['name'],
                    family['into']['method']
                )
    else:
        evo_text = 'It is not known to evolve into or from any other Pokémon\n'

    base_stats = ''
    stats = ['HP', 'Atk', 'Def', 'SpA', 'SpD', 'Spe']
    for base, minn, maxx, stat in zip(
        pkmn['base_stats'].values(),
        pkmn['min_stats'].values(),
        pkmn['max_stats'].values(),
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
    for i in pkmn['type'].values():
        typee += ' / ' + i
    typee = typee[3:]
    if '/' in typee:
        typee_str = 'Type'
    else:
        typee_str = 'Types'

    emoji_dict = t['emoji_dict']
    first_type = re.split(' / ', typee)[0]
    emoji = emoji_dict[first_type]
    name = pkmn['name']
    national = pkmn['national']
    artwork = pkmn['artwork']

    if args:
        # If True is passed in set_message, it returns all informations
        text = base_text.format(
            name, artwork, emoji, national,
            typee_str, typee, ab_str, ability,
            evo_text, gender, base_friendship, ev_yield,
            catch_rate, growth_rate, egg_groups, egg_cycles,
            species, height, weight, name_origin,
            other_lang, base_stats, legend
        )
    else:
        # Otherwise, it returns base informations
        text = base_text.format(
            name, artwork, emoji, national,
            typee_str, typee, ab_str, ability,
            evo_text, base_stats, legend
        )
    return text


def set_moveset(pkmn, form, page):
    """Set moveset message
    with page it split moveset in multiple pages of 10 moves each
    """

    # Get the range
    maxx = page * 10
    minn = maxx - 9
    index = 0

    text = t['legend'] + '\n\n'
    base_text = '<a href="{}">{}</a> <b>{}</b> ({})\n  \
        <i>{}, {}</i>\n'

    move_list = [move for move in data[pkmn][form]['moveset']]
    info_list = list(data[pkmn][form]['moveset'].values())

    for move, info in zip(move_list, info_list):
        index += 1
        if index >= minn and index <= maxx:
            if type(info['method']) == list:
                method = ''
                for i in info['method']:
                    method += ' / ' + i
                method = method[3:]
            else:
                method = info['method']
            text += base_text.format(
                data[pkmn][form]['artwork'],
                t['emoji_dict'][info['type']],
                info['name'],
                info['type'],
                info['cat'],
                method
            )

    # Number of pages. 10 moves for each page
    # So if we have 68 moves, we need 7 pages
    pages = int(index / 10) + 1

    markup = set_page_buttons(page, pages, pkmn, form)

    return {'text': text, 'markup': markup}


def get_locations(data, pkmn):
    """Get Pokémon location in every game of the core series"""

    def find_game_name(game):
        """Convert JSON format into real name"""

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
        return game

    text = ''
    form = list(data[pkmn].keys())[0]
    loc_dict = data[pkmn][form]['location']
    games = []
    locations = []
    for game, location in loc_dict.items():
        game = find_game_name(game)
        if location != 'Trade/migrate from another game':
            if location in locations:
                    # Merge games with the same location
                    for game2, location2 in zip(games, locations):
                        if location == location2:
                            games[games.index(game2)] += '/' + game
            else:
                # Initialize lists
                games.append(game)
                locations.append(location)

    for game, location in zip(games, locations):
        text += '<b>' + game + '</b>: <i>' + location + '</i>\n'

    return text


def get_usage_vgc(page, *args):
    """Get usage of Pokémon in VGC20.
    It does web scraping in the official Smogon web site with
    Pokémon Showdown usage (https://www.smogon.com/stats/)
    """

    if not args:
        # Get usage history soup
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = 'https://www.smogon.com/stats/'
        request = urllib.request.Request(url, None, headers)
        response = urllib.request.urlopen(request)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')

        # From the previous soup, find the last uploaded data
        # Then, go in VGC20 section
        link = soup.find_all('a')[-1].attrs['href']
        # 1860 in the link below is the rank
        # There are other 2 rank, but since the bot look for data every time
        # it would be very slow. So it take usage of higher rank
        url = 'https://www.smogon.com/stats/{}gen8vgc2020-1760.txt'.format(link)
        request = urllib.request.Request(url, None, headers)
        response = urllib.request.urlopen(request)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')

        # Data in the site is organized in a table
        # So RegEx are used
        txt = soup.text
        pkmn_list = re.split('\|......\|', txt)
        del pkmn_list[0]
        del pkmn_list[1]
        vgc_usage = pkmn_list
    else:
        vgc_usage = args[0]

    leaderboard = []
    maxx = page * 5
    minn = maxx - 4
    for i in range(minn, maxx+1):
        pkmn = vgc_usage[i]
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

    pages = int((len(vgc_usage)-1) / 5)
    markup = set_page_buttons(page, pages)

    return {
        'leaderboard': leaderboard,
        'markup': markup,
        'vgc_usage': vgc_usage
    }


def set_page_buttons(page, pages, *args):
    markup = types.InlineKeyboardMarkup(5)
    try:
        pkmn = args[0]
        form = args[1]
        callback_data_list = [
            'moveset/'+pkmn+'/'+form+'/1',
            'moveset/'+pkmn+'/'+form+'/'+str(page-1),
            'moveset/'+pkmn+'/'+form+'/'+str(page),
            'moveset/'+pkmn+'/'+form+'/'+str(page+1),
            'moveset/'+pkmn+'/'+form+'/'+str(pages),
            'basic_infos/'+pkmn+'/'+form
        ]
    except IndexError:
        callback_data_list = [
            'usage/'+'1',
            'usage/'+str(page-1),
            'usage/'+str(page),
            'usage/'+str(page+1),
            'usage/'+str(pages)
        ]

    # Initialize buttons
    begin = types.InlineKeyboardButton(
        text='<<1',
        callback_data=callback_data_list[0]
    )
    pre = types.InlineKeyboardButton(
        text=str(page-1),
        callback_data=callback_data_list[1]
    )
    page_button = types.InlineKeyboardButton(
        text='•'+str(page)+'•',
        callback_data=callback_data_list[2]
    )
    suc = types.InlineKeyboardButton(
        text=str(page+1),
        callback_data=callback_data_list[3]
    )
    end = types.InlineKeyboardButton(
        text=str(pages)+'>>',
        callback_data=callback_data_list[4]
    )

    # Create a page index that display, when possible,
    # First page, previous page, current page, next page, last page
    if page == pages:
        if page > 2:
            markup.add(begin, pre, page_button)
        elif page > 1:
            markup.add(pre, page_button)
        else:
            markup.add(page_button)
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
        if page < pages-1:
            markup.add(page_button, suc, end)
        else:
            markup.add(page_button, suc)

    if len(callback_data_list) == 6:
        back = types.InlineKeyboardButton(
            text='🔙 Back to basic infos',
            callback_data=callback_data_list[5]
        )
        markup.add(back)

    return markup


# /--- Bot commands ---/


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
        cid = message.message.chat.id
        mid = message.message.message_id
        pkmn = re.split('/', message.data)[1]
        form = re.split('/', message.data)[2]
        text = set_message(data[pkmn][form])
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
        pkmn = find_name(message.text)
        # Take the first form of the Pokémon
        cid = message.chat.id
        if message.text == '/data':
            text = t['error1']
        else:
            if pkmn in data:
                form = list(data[pkmn])[0]
                text = set_message(data[pkmn][form])
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
    """Show all information about the Pokémon by pressing "Expand" button"""

    cid = call.message.chat.id
    mid = call.message.message_id
    pkmn = re.split('/', call.data)[1]
    form = re.split('/', call.data)[2]
    text = set_message(data[pkmn][form], True)

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

    bot.answer_callback_query(call.id)
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

    bot.answer_callback_query(call.id)
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
        cid = message.message.chat.id
        mid = message.message.message_id
        page = re.split('/', message.data)[1]
        dictt = get_usage_vgc(int(page), usage_dict['vgc'])
    except AttributeError:
        cid = message.chat.id
        page = 1
        msg = bot.send_message(
            chat_id=cid,
            text='<i>Connecting to Pokémon Showdown database...</i>',
            parse_mode='HTML'
        )
        dictt = get_usage_vgc(int(page))
        usage_dict['vgc'] = dictt['vgc_usage']

    leaderboard = dictt['leaderboard']
    markup = dictt['markup']
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
            pkmn['rank'],
            pkmn['pokemon'],
            pkmn['usage'],
            pkmn['raw'],
            pkmn['raw%'],
            pkmn['real'],
            pkmn['real%']
        )

    bot.edit_message_text(
        text=text,
        chat_id=cid,
        message_id=msg.message_id,
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
