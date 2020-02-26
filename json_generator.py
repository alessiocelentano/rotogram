#!/usr/bin/python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib.request
import re
import json


with open('pkmn.json', 'r') as filee:
    data = json.load(filee)


headers = {'User-Agent': 'Mozilla/5.0'}
base_url = 'https://pokemondb.net/pokedex/{}'
name = input('Insert Pokémon: ')
url = base_url.format(re.sub(' ', '-', name))
url = re.sub('♀', '-f', url)  # For nidoran
url = re.sub('♂', '-m', url)  # For nidoran
request = urllib.request.Request(url, None, headers)
response = urllib.request.urlopen(request)
dataa = response.read()
soup = BeautifulSoup(dataa, 'html.parser')


# NAME
pkmn = re.sub(' ', '_', name.lower())
data[pkmn] = {}


# FORMS
forms_table = soup.find(
    'div', {
        'class': 'tabs-tab-list'
    }
)
forms_list = [i.text for i in forms_table.find_all('a')]


# DEX, TYPING, SPECIES, HEIGHT, WEIGHT AND ABILITIES
pokedex_data_list = soup.find_all(
    'div', {
        'class': 'grid-col span-md-6 span-lg-4'
    }
)
del pokedex_data_list[0]  # Ads space, no data

for pokedex_data, form in zip(pokedex_data_list, forms_list):
    form = re.sub(' ', '_', form.lower())
    data[pkmn][form] = {}
    keys_list = pokedex_data.find_all('th')
    for key in keys_list:
        value = key.findNext('td')
        key = re.sub('[\u2116 ]', '', key.text.lower())

        if key == 'abilities':
            data[pkmn][form][key] = {}
            index = 1  # Number the abilities
            if value.text != '—':  # For Partner Pikachu/Eevee
                for ability in value.span.find_all('a'):
                    ability = ability.text
                    data[pkmn][form][key]['ability' + str(index)] = ability
                    index += 1
                if value.small:
                    for ability in value.small.find('a'):
                        data[pkmn][form][key]['hidden_ability'] = ability
                        # No increment because Hidden Abilities aren't numered

        elif key == 'local':  # Dex number of each region
            data[pkmn][form][key] = {}
            dex_num_list = re.findall('[0-9][0-9][0-9]', value.text)
            for game, num in zip(value.find_all('small'), dex_num_list):
                game = re.sub('[^A-Z0-9]', '', game.text).lower()
                if 'sm' in game or 'usum' in game:
                    game = game[:-1]
                    # Delete the "Alola dex" part
                elif 'xy' in game:
                    game = 'xy'
                    # Delete the part of Kalos
                    # e.g. Central, Coustal and Mountain
                elif game == 'lgplge':
                    game = 'lgpe'
                elif game == 'p':
                    game = 'pt'
                elif game == 'ss':
                    game = 'swsh'
                data[pkmn][form][key][game] = num

        elif key == 'type':
            value = value.text[1:-1]  # Delete useless characters
            types_list = re.split(' ', value)
            data[pkmn][form][key] = {}
            data[pkmn][form][key]['type1'] = types_list[0]
            if len(types_list) > 1:
                data[pkmn][form][key]['type2'] = types_list[1]

        elif key == 'height' or key == 'weight':
            values = re.split(' ', value.text)
            data[pkmn][form][key] = {}
            data[pkmn][form][key]['si'] = values[0]
            data[pkmn][form][key]['usc'] = re.sub('[()]', '', values[1])

        else:
            data[pkmn][form][key] = re.sub('\n', '', value.text)


# STATS
all_stats = soup.find_all(
    'div', {
        'class': 'grid-col span-md-12 span-lg-8'
    }
)
key_list = ['hp', 'atk', 'def', 'spa', 'spd', 'spe']
values_list = []
total_list = []  # Sum of the 6 stats
for stats in all_stats:
    if stats != all_stats[-1]:  # The last one element is the position
        stats_list = stats.find_all(
            'td', {
                'class': 'cell-num'
            }
        )
        values = [value.text for value in stats_list]
        values_list.append(values)
        total_list.append(
            stats.find(
                'td', {
                    'class': 'cell-total'
                }
            ).text
        )
for form in forms_list:
    form = re.sub(' ', '_', form).lower()
    data[pkmn][form]['base_stats'] = {}
    data[pkmn][form]['min_stats'] = {}
    data[pkmn][form]['max_stats'] = {}
    stats = key_list.copy()
    while values_list[0]:
        data[pkmn][form]['base_stats'][stats[0]] = values_list[0].pop(0)
        data[pkmn][form]['min_stats'][stats[0]] = values_list[0].pop(0)
        data[pkmn][form]['max_stats'][stats.pop(0)] = values_list[0].pop(0)
    del values_list[0]
    data[pkmn][form]['base_stats']['total'] = total_list.pop(0)


# EV yield, cath rate, base friendship, base exp and growth rate
# Egg groups, gender and egg cycles
data_list = soup.find_all(
    'div', {
        'class': 'grid-col span-md-6 span-lg-12'
    }
)
index = 0  # For iterate forms_list
count = 0  # For increment index
for i in data_list:
    if count == 2:
        index += 1
        count = 0
    key_list = i.find_all('th')
    value_list = i.find_all('td')
    for key, value in zip(key_list, value_list):
        form = re.sub(' ', '_', forms_list[index].lower())
        key = re.sub(' ', '_', key.text.lower()).replace('.', '')
        if key in ['ev_yield', 'growth_rate', 'egg_groups']:
            if key == 'growth_rate':
                data[pkmn][form][key] = value.text
            else:
                if '—' not in value.text:  # For Partner Pikachu/Eevee
                    data[pkmn][form][key] = []
                    for stat in re.split(', ', value.text[1:-1]):
                        data[pkmn][form][key].append(stat)
        elif key == 'gender':
            data[pkmn][form][key] = value.text
        else:
            value = value.text.replace('\n', '')
            data[pkmn][form][key] = re.split(' ', value)[0]
    count += 1


# Evolutions
def find_name(pkmn):
    if len(pkmn.find_all('small')) == 3:
        pkmn_name = pkmn.find_all('small')[-2].text
    else:
        pkmn_name = pkmn.find_all('a')[1].text
    return pkmn_name


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
target_list = []
for line in lines:
    pkmns = line.find_all(
        'div', {
            'class': 'infocard'
        }
    )
    for pkmnn in pkmns:
        pkmn_name = find_name(pkmnn)
        if pkmn_name in forms_list:
            if pkmnn not in target_list:
                next_methods_list = []
                next_pkmns_list = []
                form = re.sub(' ', '_', find_name(pkmnn).lower())
                data[pkmn][form]['evo'] = {}
            target_list.append(pkmnn)
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
            pre_evo = find_name(pre_evo)
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
                    next_method = re.sub('[()]', '', next_method.small.text)
                    next_pkmn = find_name(next_pkmn)
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
            next_method = re.sub('[()]', '', next_method.small.text)
            next_pkmn = find_name(next_pkmn)
            next_methods_list.append(next_method)
            next_pkmns_list.append(next_pkmn)
        if not next_methods_list:
            next_methods_list = None
        elif len(next_methods_list) == 1:
            next_methods_list = next_methods_list[0]
        if not next_pkmns_list:
            next_pkmns_list = None
        elif len(next_pkmns_list) == 1:
            next_pkmns_list = next_pkmns_list[0]
        target_text = re.sub(' ', '_', find_name(target).lower())
        data[pkmn][target_text]['evo']['from'] = {
            'evo': pre_evo,
            'method': pre_method
        }
        data[pkmn][target_text]['evo']['into'] = {
            'evo': next_pkmns_list,
            'method': next_methods_list
        }


with open('pkmn.json', 'w') as filee:
    json.dump(data, filee, indent=4)
