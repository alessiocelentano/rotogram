#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import json
import urllib

from bs4 import BeautifulSoup


def find_name(pkmn):
    """ A simply function for find the Pokémon name by HTML snippet (pkmn) """
    if len(pkmn.find_all('small')) == 3:
        pkmn_name = pkmn.find_all('small')[-2].text
    else:
        try:
            pkmn_name = pkmn.find_all('a')[1].text
        except IndexError:
            pkmn_name = pkmn.text
    pkmn_name = re.sub(' ', '_', pkmn_name.lower())
    return pkmn_name


def find_acronym(game):
    game = re.sub('[^A-Z0-9]', '', game.text).lower()
    # Delete the area of Kalos
    # e.g. Central, Coustal and Mountain
    if 'xy' in game:
        game = 'xy'
    # Delete the "Alola dex" part
    elif 'sm' in game or 'usum' in game:
        if game != 'sm' and game != 'usum':
            game = game[:-1]
    # Just edit it in the right acronym
    elif game == 'rb':
        game = 'redblue'
    elif game == 'y':
        game = 'yellow'
    elif game == 'gs':
        game = 'goldsilver'
    elif game == 'c':
        game = 'crystal'
    elif game == 'rs':
        game = 'rubysapphire'
    elif game == 'e':
        game = 'emerald'
    elif game == 'dp':
        game = 'diamondpearl'
    elif game == 'p':
        game = 'platinum'
    elif game == 'lgplge':
        game = 'lgpe'
    elif game == 'ss':
        game = 'swsh'

    return game


with open('dist/pkmn.json', 'r') as f:
    data = json.load(f)
with open('dist/pkmn.txt', 'r') as f:
    pokemon_list = f.readlines()
print('\nPokémon \t| Percentage')
perc_index = 0

for pokemon in pokemon_list:
    # Get Pokémon page HTML
    # Credits: PokémonDB (https://pokemondb.net)
    perc_index += 1
    general_percentage = '{0:.2f}%'.format(perc_index/8.9)
    name = pokemon[:-1]
    print(name + '    \t| ' + str(general_percentage))
    pokemon = re.sub(' ', '-', pokemon[:-1])
    pokemon = re.sub('♀', '-f', pokemon)  # For Nidoran♀
    pokemon = re.sub('♂', '-m', pokemon)  # For Nidoran♂
    pokemon = re.sub('é', 'e', pokemon)  # For Flabébé
    pokemon = re.sub('[^A-Za-z-]', '', pokemon)

    headers = {'User-Agent': 'Mozilla/5.0'}
    base_url = 'https://pokemondb.net/pokedex/{}'
    url = base_url.format(pokemon)
    request = urllib.request.Request(url, None, headers)
    response = urllib.request.urlopen(request)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')

    # Name
    pkmn = re.sub('[ -]', '_', pokemon.lower())
    data[pkmn] = {'name': name}

    # Forms
    form_tab = soup.find(
        'div', {
            'class': 'tabs-tab-list'
        }
    )
    form_text = form_tab.find_all('a')
    form_list = [re.sub(' ', '_', i.text.lower()) for i in form_text]
    if len(form_list) > 1:
        have_forms = True
    else:
        have_forms = False
    forms = {}
    for form in form_list:
        forms[form] = {}

    # Artwork
    artwork_list = soup.find_all(
        'div', {
            'class': 'grid-col span-md-6 span-lg-4 text-center'
        }
    )
    for artwork, form in zip(artwork_list, form_list):
        if artwork.find('img'):
            artwork = artwork.find('img').attrs['src']
            artwork = re.sub('artwork', 'artwork/large', artwork)
        else:
            continue
        forms[form]['artwork'] = artwork

    # Dex, Typing, Species, Height, Weight and abilities
    pokedex_data_list = soup.find_all(
        'div', {
            'class': 'grid-col span-md-6 span-lg-4'
        }
    )
    del pokedex_data_list[0]  # Ads space, no data

    for pokedex_data, form in zip(pokedex_data_list, form_list):
        form = re.sub(' ', '_', form.lower())
        keys_list = pokedex_data.find_all('th')

        for key in keys_list:
            value = key.findNext('td')
            key = re.sub('[\u2116 ]', '', key.text.lower())

            if key == 'abilities':
                forms[form][key] = {}
                index = 1  # To number the abilities
                if value.text != '—':  # For Partner Pikachu/Eevee
                    ability_list = value.span.find_all('a')
                    for ability in ability_list:
                        ability = ability.text
                        forms[form][key]['ability' + str(index)] = ability
                        index += 1
                    if value.small:
                        ha = value.small.a.text
                        forms[form][key]['hidden_ability'] = ha

            # Dex number of each region
            elif key == 'local':
                data[pkmn][key] = {}
                local_list = re.findall('[0-9][0-9][0-9]', value.text)
                game_list = value.find_all('small')
                for game, local in zip(game_list, local_list):
                    game = find_acronym(game)
                    data[pkmn][key][game] = local

            elif key == 'type':
                value = value.text[1:-1]  # Delete useless characters
                type_list = re.split(' ', value)
                forms[form][key] = {}
                forms[form][key]['type1'] = type_list[0]
                if len(type_list) > 1:
                    forms[form][key]['type2'] = type_list[1]

            elif key == 'height' or key == 'weight':
                value = re.split(' ', value.text)
                forms[form][key] = {}
                try:
                    forms[form][key]['si'] = value[0]
                    forms[form][key]['usc'] = re.sub('[()]', '', value[1])
                except IndexError:
                    forms[form][key]['si'] = None
                    forms[form][key]['usc'] = None

            else:
                value = re.sub('\n', '', value.text)
                data[pkmn][key] = value

    # EV yield, cath rate, base friendship, base exp and growth rate
    # Egg groups, gender and egg cycles
    data_list = soup.find_all(
        'div', {
            'class': 'grid-col span-md-6 span-lg-12'
        }
    )
    index = 0  # For iterate form_list
    count = 0  # For increment index

    for dataa in data_list:
        if count == 2:
            index += 1
            count = 0

        line_list = dataa.find_all('tr')
        for line in line_list:
            key = line.find('th').text
            key = re.sub(' ', '_', key.lower())
            value = line.find('td').text
            form = re.sub(' ', '_', form_list[index].lower())

            if key == 'ev_yield':
                forms[form][key] = []
                value = re.split(', ', value[1:-1])
                for stat in value:
                    forms[form][key].append(stat)

            elif key == 'base_exp':
                forms[form][key] = []
                for stat in value:
                    forms[form][key].append(stat)

            else:
                if key not in data[pkmn]:
                    if key in ['egg_groups']:
                        if value == '—':  # For Partner Pikachu/Eevee
                            data[pkmn][key] = None
                        else:
                            data[pkmn][key] = []
                            value = re.split(', ', value[1:-1])
                            for stat in value:
                                data[pkmn][key].append(stat)

                    elif key == 'gender':
                        data[pkmn][key] = []
                        value = re.split(', ', value)
                        for stat in value:
                            data[pkmn][key].append(stat)

                    elif key in [
                        'catch_rate', 'base_friendship',
                        'growth_rate', 'egg_cycles'
                    ]:
                        data[pkmn][key] = value

        count += 1

    # Stats
    tmp = soup.find_all(
        'div', {
            'id': 'dex-stats'
        }
    )
    key_list = ['hp', 'atk', 'def', 'spa', 'spd', 'spe']
    value_list = []
    total_list = []
    for i in tmp:
        values = []
        table = i.find_next('table')
        stats_list = table.find_all('tr')

        for stat in stats_list:
            if stat == stats_list[-1]:
                try:
                    total_list.append(stat.b.text)
                except AttributeError:
                    continue
            else:
                stat_list = stat.find_all(
                    'td', {
                        'class': 'cell-num'
                    }
                )
                value = [value.text for value in stat_list]
                values.append(value)
        value_list.append(values)

    for form, value in zip(form_list, value_list):
        try:
            form = re.sub(' ', '_', form).lower()
            stats = key_list.copy()
            forms[form]['base_stats'] = {}
            forms[form]['min_stats'] = {}
            forms[form]['max_stats'] = {}
            while value:
                forms[form]['base_stats'][stats[0]] = value[0].pop(0)
                forms[form]['min_stats'][stats[0]] = value[0].pop(0)
                forms[form]['max_stats'][stats.pop(0)] = value[0].pop(0)
                del value[0]
            forms[form]['base_stats']['total'] = total_list.pop(0)
        except IndexError:
            continue

    # Evolutions
    tmp = soup.find(
        'div', {
            'id': 'dex-evolution'
        }
    )
    lines = tmp.find_next_siblings(
        'div', {
            'class': 'infocard-list-evo'
        }
    )

    for form in form_list:
        forms[form]['evolutions'] = {}

    for line in lines:
        target_list = []
        in_this_line = False
        pkmns = line.find_all(
            'div', {
                'class': 'infocard'
            }
        )
        for pkmnn in pkmns:
            pkmn_name = find_name(pkmnn)
            if pkmn_name in form_list:
                in_this_line = True
                if target_list:
                    if pkmnn == target_list[-1]:
                        target_list[-1] = pkmnn
                    elif pkmnn == pkmns[0]:
                        target_list = []
                if pkmnn not in target_list:
                    next_methods_list = []
                    next_pkmns_list = []
                    target_list.append(pkmnn)
                    form = re.sub(' ', '_', find_name(pkmnn).lower())

        if in_this_line:
            for target in target_list:
                pre_method = target.find_previous_sibling(
                    'span', {
                        'class': 'infocard-arrow'
                    }
                )
                if pre_method:
                    pre_evo = target.find_previous_sibling(
                        'div', {
                            'class': 'infocard'
                        }
                    )
                    if not pre_evo:
                        tmp = line.find(
                            'span', {
                                'class': 'infocard-evo-split'
                            }
                        )
                        pre_evo = tmp.find_previous_sibling(
                            'div', {
                                'class': 'infocard'
                            }
                        )
                    pre_method = re.sub('[()]', '', pre_method.small.text)
                    pre_method = re.sub('_', ' ', pre_method.title())
                    pre_evo = find_name(pre_evo)
                    pre_evo = re.sub('_', ' ', pre_evo.title())
                else:
                    pre_method, pre_evo = None, None
                next_method = target.find_next_sibling(
                    'span', {
                        'class': 'infocard-arrow'
                    }
                )
                if not next_method:
                    tmp = target.find_next_sibling()
                    if tmp:
                        branches = tmp.find_all(
                            'div', {
                                'class': 'infocard-list-evo'
                            }
                        )
                        for branch in branches:
                            next_method = branch.find(
                                'span', {
                                    'class': 'infocard-arrow'
                                }
                            )
                            next_pkmn = branch.find(
                                'div', {
                                    'class': 'infocard'
                                }
                            )
                            next_method = next_method.small.text
                            next_method = re.sub('[()]', '', next_method)
                            next_pkmn = find_name(next_pkmn)
                            next_pkmn = re.sub('_', ' ', next_pkmn.title())
                            next_methods_list.append(next_method)
                            next_pkmns_list.append(next_pkmn)
                else:
                    next_method = target.find_next(
                        'span', {
                            'class': 'infocard-arrow'
                        }
                    )
                    next_pkmn = target.find_next(
                        'div', {
                            'class': 'infocard'
                        }
                    )
                    next_method = next_method.small.text
                    next_method = re.sub('[()]', '', next_method)
                    next_pkmn = find_name(next_pkmn)
                    next_pkmn = re.sub('_', ' ', next_pkmn.title())
                    next_methods_list.append(next_method)
                    next_pkmns_list.append(next_pkmn)

                if not next_methods_list:
                    next_method = None
                elif len(next_methods_list) == 1:
                    next_method = next_methods_list[0].title()
                else:
                    next_method = [i.title() for i in next_methods_list]
                if not next_pkmns_list:
                    next_pkmn = None
                elif len(next_pkmns_list) == 1:
                    next_pkmn = next_pkmns_list[0].title()

                else:
                    next_pkmn = next_pkmns_list
                target_text = re.sub(' ', '_', find_name(target).lower())

                forms[target_text]['evolutions']['from'] = {
                    'name': pre_evo,
                    'method': pre_method
                }
                forms[target_text]['evolutions']['into'] = {
                    'name': next_pkmn,
                    'method': next_method
                }

    # Changes
    changes_list = soup.find_all('h3')
    changes_list = [i for i in changes_list if 'changes' in i.text]
    for form, changes in zip(form_list, changes_list):
        form = re.sub(' ', '_', form.lower())
        data[pkmn]['changes'] = []
        changes = changes.find_next('ul').find_all('li')
        for change in changes:
            data[pkmn]['changes'].append(change.text)

    # Pokédex entries
    tmp = soup.find(
        'div', {
            'id': 'dex-flavor'
        }
    )
    div_list = tmp.find_next_siblings(
        'div', {
            'class': 'resp-scroll'
        }
    )

    for div in div_list:
        table = div.find('table')
        if table.attrs == {'class': ['vitals-table']}:
            form = div.find_previous('h3')
            if form:
                form = re.sub(' ', '_', form.text.lower())
                if form == 'darmanitan':
                    form = 'standard_mode'
                if form not in forms:
                    forms[form] = {}
                forms[form]['dex_entries'] = {}
                entries_list = table.find_all('tr')
                for entry in entries_list:
                    games = entry.find_all('span')
                    for game in games:
                        game = re.sub('[ \']', '', game.text.lower())
                        entry_text = entry.find('td').text
                        forms[form]['dex_entries'][game] = entry_text
        else:
            break

    # Location
    data[pkmn]['location'] = {}
    div = soup.find_all(
        'div', {
            'class': 'grid-col span-md-12 span-lg-8'
        }
    )[-1]
    lines = div.find_all('tr')
    for line in lines:
        games_list = line.find_all('span')
        location = line.find('td')
        for game in games_list:
            game = re.sub('[ \']', '', game.text.lower())
            data[pkmn]['location'][game] = location.text

    # Name in other languages
    data[pkmn]['other_lang'] = {}
    div = soup.find(
        'div', {
            'class': 'grid-col span-md-12 span-lg-6'
        }
    )
    lines = div.find_all('tr')
    for line in lines:
        lang = line.find('th').text.lower()
        translation = line.find('td').text
        data[pkmn]['other_lang'][lang] = translation

    # Name origin
    data[pkmn]['name_origin'] = {}
    div = soup.find_all(
        'div', {
            'class': 'grid-col span-md-12 span-lg-6'
        }
    )[-1]
    origin_list = div.find_all('dt')
    descrip_list = div.find_all('dd')
    for origin, descrip in zip(origin_list, descrip_list):
        origin = origin.text.lower()
        descrip = descrip.text
        data[pkmn]['name_origin'][origin] = descrip

    # Moveset
    tmp = soup.find_all(
            'div', {
                'class': 'tabset-moves-game-form'
            }
        )
    if tmp:
        multiple_forms = True
    else:
        multiple_forms = False

    games_tab_wrapper = soup.find(
        'div', {
            'class': 'tabset-moves-game tabs-wrapper'
        }
    )
    games_tab = games_tab_wrapper.find('div')
    games = games_tab.find_all('a')
    all_moves = games_tab.find_next('div')
    move_tabs = all_moves.find_all(
        'div', {
            'class': 'tabs-panel'
        }
    )

    for game, tab in zip(games, move_tabs):
        game = find_acronym(game)
        data_methods = tab.find_all('h3')
        for method in data_methods:
            zone = method.find_next_sibling('div')
            p = method.find_next_sibling('p')
            if p.attrs == {'class': ['text-small']}:
                if multiple_forms:
                    if 'tabset-moves-game-form' in zone.attrs.values():
                        # Have multiple forms for this method
                        form_tabs = zone.find('div')
                        all_forms = form_tabs.find_all('a')
                        form_tab_list = [find_name(i) for i in all_forms]
                        move_tabs = form_tabs.find_next('div')
                        move_list = move_tabs.find_all('table')
                    else:
                        form_tab_list = form_list
                        move_list = []
                        for i in form_tab_list:
                            move_list.append(zone.find('table'))
                else:
                    form_tab_list = [pkmn]
                    move_list = [zone.find('table')]

                for form, moves in zip(form_tab_list, move_list):
                    if form == 'darmanitan':
                        form = 'standard_mode'
                    if form not in forms:
                        forms[form] = {}
                    if 'moveset' not in forms[form]:
                        forms[form]['moveset'] = {}
                    if game not in forms[form]['moveset']:
                        forms[form]['moveset'][game] = {}
                    if method.text == 'Moves learnt by level up':
                        method_text = 'level_up'
                    elif method.text == 'Egg moves':
                        method_text = 'egg_moves'
                    elif method.text == 'Move Tutor moves':
                        method_text = 'move_tutor'
                    elif method.text == 'Pre-evolution moves':
                        method_text = 'pre_evo_moves'
                    elif method.text == 'Moves learnt by TM':
                        method_text = 'tm'
                    elif method.text == 'Special moves':
                        method_text = 'special_moves'
                    elif method.text == 'Transfer-only moves':
                        method_text = 'transfer_only'
                    elif method.text == 'Moves learnt by TR':
                        method_text = 'tr'
                    elif method.text == 'Moves learnt by HM':
                        method_text = 'hm'

                    cols = moves.find_all('th')
                    lines = moves.find_all('tr')
                    del lines[0]
                    for line in lines:
                        move = line.find(
                            'td', {
                                'class': 'cell-name'
                            }
                        )
                        move = re.sub(' ', '_', move.text.lower())
                        value_list = line.find_all('td')
                        for col, value in zip(cols, value_list):
                            key = re.sub('[.]', '', col.text.lower())
                            if value.find('img'):
                                value = value.img.attrs['title']
                            elif value.find('span'):
                                value = value.span.attrs['title']
                            elif value.text == '\u2014':
                                value = None
                            else:
                                value = value.text
                            if method_text not in forms[form]['moveset'][game]:
                                forms[form]['moveset'][game][method_text] = {}
                            if move not in forms[form]['moveset'][game][method_text]:
                                forms[form]['moveset'][game][method_text][move] = {}
                            forms[form]['moveset'][game][method_text][move][key] = value

    # Add forms dictionary at the end of the JSON
    # for more readibility
    if have_forms:
        data[pkmn]['forms'] = forms
    else:
        for key, value in forms[pkmn].items():
            data[pkmn][key] = value

    with open('dist/pkmn.json', 'w') as f:
        json.dump(data, f, indent=4)
