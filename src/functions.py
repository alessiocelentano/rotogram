import json
import re
import urllib

from pyrogram import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup


texts = json.load(open('src/texts.json', 'r'))
data = json.load(open('src/pkmn.json', 'r'))


def bot_action(app, message, text, markup):
    try:
        app.edit_message_text(
            chat_id=message.message.chat.id,
            text=text,
            message_id=message.message.message_id,
            parse_mode='HTML',
            reply_markup=markup
        )
        app.answer_callback_query(message.id)
    except AttributeError:
        app.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode='HTML',
            reply_markup=markup
        )


def find_name(pkmn):
    pkmn = pkmn.lower()
    pkmn = re.sub('♀', '_f', pkmn)  # For Nidoran♀
    pkmn = re.sub('♂', '_m', pkmn)  # For Nidoran♂
    pkmn = re.sub('[èé]', 'e', pkmn)  # For Flabébé
    pkmn = re.sub('/data(@RotomgramBot)* ', '', pkmn)
    pkmn = re.sub('[ -]', '_', pkmn)
    pkmn = re.sub('[^a-z_]', '', pkmn)
    return pkmn


def check_name(pkmn, data):
    # Valid input: Pokemon
    if pkmn in data:
        form = list(data[pkmn].keys())[0] # Basically first form
        return {'pkmn': pkmn, 'form': list(data[pkmn].keys())[0]}

    # Valid input: Pokemon form
    for key in data:
        for form in data[key]:
            if form == pkmn:
                return {'pkmn': key, 'form': form}

    # Invalid input: characters limit
    if len(pkmn) > 25:
        return texts['limit']

    # Otherwise, it returns three best matches
    return best_matches(pkmn, data)


def best_matches(pkmn, data):
    score_dict = {}
    for key in data:
        for form in data[key]:
            if key not in form:
                name = key + ' ' + form
            else:
                name = form
            score1 = 0
            score2 = 0

            # SCORE 1
            # Typing errors
            for letter, letter2 in zip(name, pkmn):
                if letter == letter2:
                    score1 += 100/len(name)

            # SCORE 2
            # Additional characters
            input_index = 0
            data_index = 0
            while input_index < len(pkmn):
                if pkmn[input_index] == name[data_index]:
                    if len(pkmn) > len(name):
                        score2 += 100/len(pkmn)
                    else:
                        score2 += 100/len(name)
                    data_index += 1
                input_index += 1
             
            if score1 > score2:
                score_dict[key+'/'+form] = score1
            else:
                score_dict[key+'/'+form] = score2

    for key, value in list(score_dict.items()):
        if value < 5:
            del score_dict[key]
    if len(score_dict) < 3:
        return texts['nomatch']

    result = []
    while len(result) < 3:
        maxx = 0
        max_dict = {}
        for pkmn, score in list(score_dict.items()):
            if score > maxx:
                max_dict = {pkmn: score}
                maxx = score
        for key, value in list(max_dict.items()):
            del score_dict[key]
            pkmn = re.split('/', key)[0]
            form = re.split('/', key)[1]
            percentage = str('%.2f' % value) + '%'
            result.append({
                'pkmn': pkmn,
                'form': form,
                'percentage': percentage}
            )
    return result


def form_name(pkmn, form):
    pkmn = re.sub('_', ' ', pkmn.title())
    if pkmn in ['Ho Oh', 'Jangmo O', 'Hakamoo O', 'Kommo O']:
        pkmn = re.sub(' ', '-', pkmn[:-1]+pkmn[-1].lower())
    elif pkmn == 'Nidoran F':
        pkmn = 'Nidoran♀'
    elif pkmn == 'Nidoran M':
        pkmn = 'Nidoran♂'
    if pkmn in form:
        result = form
    else:
        result = pkmn + ' (' + form + ')'
    return result


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


def get_base_data(pkmn, pkmn_name):
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
    legend = texts['minmax']

    typee = ''
    for i in pkmn['type'].values():
        typee += ' / ' + i
    typee = typee[3:]
    if '/' in typee:
        typee_str = 'Type'
    else:
        typee_str = 'Types'

    if pkmn_name:
        if type(pkmn_name) != str:
            pkmn_name = pkmn['name']
    else:
        pkmn_name = pkmn['name']
    emoji_dict = texts['emoji_dict']
    first_type = re.split(' / ', typee)[0]
    emoji = emoji_dict[first_type]
    national = pkmn['national']
    artwork = pkmn['artwork']

    return {
        'ability': ability,
        'ab_str': ab_str,
        'evo_text': evo_text,
        'base_stats': base_stats,
        'legend': legend,
        'typee': typee,
        'typee_str': typee_str,
        'name': pkmn_name,
        'emoji': emoji,
        'national': national,
        'artwork': artwork
    }


def get_advanced_data(pkmn):
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

    return {
        'base_friendship': base_friendship,
        'catch_rate': catch_rate,
        'growth_rate': growth_rate,
        'egg_cycles': egg_cycles,
        'species': species,
        'gender': gender,
        'ev_yield': ev_yield,
        'egg_group': egg_groups,
        'other_lang': other_lang,
        'name_origin': name_origin,
        'height': height,
        'weight': weight
    }


def set_message(pkmn, reduced=None, *args):
    if reduced:
        text = texts['reduced_text']
        base_data = get_base_data(pkmn, args)
        return text.format(**base_data)
    else:
        text = texts['expanded_text']
        base_data = get_base_data(pkmn, args)
        advanced_data = get_advanced_data(pkmn)
        return text.format(**base_data, **advanced_data)


def set_moveset(pkmn, form, page):
    maxx = page * 10
    minn = maxx - 9
    index = 0

    text = texts['legend'] + '\n\n'
    base_text = texts['moveset']

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
                texts['emoji_dict'][info['type']],
                info['name'],
                info['type'],
                info['cat'],
                method
            )

    pages = int(index // 10)
    pages += 1 if pages % 10 != 0 else 0
    markup = set_page_buttons(page, pages, pkmn, form)
    return {'text': text, 'markup': markup}


def find_game_name(game):
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


def get_locations(data, pkmn):
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
    if not args:
        # Get usage history soup
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = 'https://www.smogon.com/stats/'
        request = urllib.request.Request(url, None, headers)
        response = urllib.request.urlopen(request)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')

        link = soup.find_all('a')[-1].attrs['href']
        # 1760 in the link below is the rank
        # There are other 2 rank, but since the bot look for data every time
        # it would be very slow. So it take usage of higher rank
        url = 'https://www.smogon.com/stats/{}gen8vgc2020-1760.txt'.format(link)
        request = urllib.request.Request(url, None, headers)
        response = urllib.request.urlopen(request)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')

        # Data in the site is organized in a table
        txt = soup.text
        pkmn_list = re.split('\|......\|', txt)
        del pkmn_list[0]
        del pkmn_list[1]
        vgc_usage = pkmn_list
    else:
        vgc_usage = args[0]

    leaderboard = []
    maxx = page * 15
    minn = maxx - 14
    for i in range(minn, maxx+1):
        pkmn = vgc_usage[i]
        pkmn = re.sub(' ', '', pkmn)
        stats = re.split('\|', pkmn)
        usage = str('%.2f' % float(stats[1][:-1])) + '%'
        dictt = {
            'rank': i,
            'pokemon': stats[0],
            'usage': usage,
        }
        leaderboard.append(dictt)

    pages = int((len(vgc_usage)-1) / 15)
    markup = set_page_buttons(page, pages)

    return {
        'leaderboard': leaderboard,
        'markup': markup,
        'vgc_usage': vgc_usage
    }


def set_page_buttons(page, pages, *args):
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
    markup_list = []
    begin = InlineKeyboardButton(
        text='<<1',
        callback_data=callback_data_list[0]
    )
    pre = InlineKeyboardButton(
        text=str(page-1),
        callback_data=callback_data_list[1]
    )
    page_button = InlineKeyboardButton(
        text='•'+str(page)+'•',
        callback_data=callback_data_list[2]
    )
    suc = InlineKeyboardButton(
        text=str(page+1),
        callback_data=callback_data_list[3]
    )
    end = InlineKeyboardButton(
        text=str(pages)+'>>',
        callback_data=callback_data_list[4]
    )

    # Create a page index that display, when possible,
    # First page, previous page, current page, next page, last page
    markup_list.append([])
    if 1 < page-1:
        markup_list[-1].append(begin)
    if page != 1:
        markup_list[-1].append(pre)
    if markup_list[-1] or page != pages:
        markup_list[-1].append(page_button)
    if page != pages:
        markup_list[-1].append(suc)
    if pages > page+1:
        markup_list[-1].append(end)
    if not markup_list[-1]:
        markup_list.remove(markup_list[-1])

    if len(callback_data_list) == 6:
        markup_list.append([
            InlineKeyboardButton(
                text='🔙 Back to basic infos',
                callback_data=callback_data_list[5]
            )
        ])

    return InlineKeyboardMarkup(markup_list)
